"""Phân loại lỗi LLM thành quyết định failover không làm lộ provider detail."""

from dataclasses import dataclass
from enum import StrEnum

import httpx
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
)
from pydantic import ValidationError
from src.common.exceptions.error_codes import ErrorCode

GOOGLE_ERROR_TYPES: tuple[type[Exception], ...]


def _google_error_types() -> tuple[type[Exception], ...]:
    types: list[type[Exception]] = []
    try:
        from google.genai.errors import APIError as GoogleGenAiError

        types.append(GoogleGenAiError)
    except ImportError:
        pass
    try:
        from google.api_core.exceptions import GoogleAPICallError

        types.append(GoogleAPICallError)
    except ImportError:
        pass
    return tuple(types)


GOOGLE_ERROR_TYPES = _google_error_types()


class LlmFailureAction(StrEnum):
    """Hành động hạ tầng sau khi phân loại lỗi provider."""

    FAIL = "FAIL"
    ROTATE = "ROTATE"
    DISABLE_AND_ROTATE = "DISABLE_AND_ROTATE"


@dataclass(frozen=True, slots=True)
class LlmFailureDecision:
    """Kết quả phân loại chỉ chứa metadata an toàn."""

    action: LlmFailureAction
    code: ErrorCode
    reason: str


class LlmFailureClassifier:
    """Ưu tiên type/status chính thức rồi mới dùng fallback message giới hạn."""

    def classify(self, exc: Exception) -> LlmFailureDecision:
        """Phân loại một exception provider hoặc structured parser."""
        if isinstance(exc, (AuthenticationError, PermissionDeniedError)):
            return _disable(ErrorCode.LLM_AUTHENTICATION_ERROR, "authentication")
        if isinstance(exc, RateLimitError):
            return self._rate_limit_decision(exc.body)
        if isinstance(exc, NotFoundError):
            return _fail(ErrorCode.LLM_MODEL_NOT_FOUND, "model_not_found")
        if isinstance(exc, GOOGLE_ERROR_TYPES):
            return self._google_decision(exc)
        if isinstance(exc, (APITimeoutError, APIConnectionError, httpx.TransportError)):
            return _fail(ErrorCode.LLM_TIMEOUT_ERROR, "transient_network")
        if isinstance(exc, (TimeoutError, ConnectionError)):
            return _fail(ErrorCode.LLM_TIMEOUT_ERROR, "transient_network")
        if isinstance(exc, ValidationError) or "outputparser" in type(exc).__name__.casefold():
            return _fail(ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR, "structured_output")
        return self._fallback_decision(exc)

    def _google_decision(self, exc: Exception) -> LlmFailureDecision:
        status_code = _google_status_code(exc)
        if status_code in {401, 403}:
            return _disable(ErrorCode.LLM_AUTHENTICATION_ERROR, "authentication")
        if status_code == 404:
            return _fail(ErrorCode.LLM_MODEL_NOT_FOUND, "model_not_found")
        if status_code == 429:
            return self._rate_limit_decision(getattr(exc, "details", exc))
        if status_code == 408:
            return _fail(ErrorCode.LLM_TIMEOUT_ERROR, "transient_network")
        return _fail(ErrorCode.LLM_ERROR, "provider_error")

    def _rate_limit_decision(self, detail: object) -> LlmFailureDecision:
        if _contains_quota_marker(detail):
            return _disable(ErrorCode.LLM_QUOTA_EXCEEDED, "quota_exhausted")
        return LlmFailureDecision(LlmFailureAction.ROTATE, ErrorCode.LLM_RATE_LIMIT_ERROR, "rate_limit")

    def _fallback_decision(self, exc: Exception) -> LlmFailureDecision:
        message = str(exc).casefold()
        if _contains_any(message, ("invalid api key", "api key expired", "revoked", "unauthorized")):
            return _disable(ErrorCode.LLM_AUTHENTICATION_ERROR, "authentication")
        if _contains_quota_marker(message):
            return _disable(ErrorCode.LLM_QUOTA_EXCEEDED, "quota_exhausted")
        if _contains_any(message, ("rate limit", "resource_exhausted", "resourceexhausted")):
            return LlmFailureDecision(LlmFailureAction.ROTATE, ErrorCode.LLM_RATE_LIMIT_ERROR, "rate_limit")
        if _contains_any(message, ("404", "not found", "not_found")):
            return _fail(ErrorCode.LLM_MODEL_NOT_FOUND, "model_not_found")
        if _contains_any(message, ("timeout", "timed out", "connection reset")):
            return _fail(ErrorCode.LLM_TIMEOUT_ERROR, "transient_network")
        if "validation" in message:
            return _fail(ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR, "structured_output")
        return _fail(ErrorCode.LLM_ERROR, "provider_error")


def _contains_quota_marker(detail: object) -> bool:
    markers = (
        "insufficient_quota",
        "quota_exceeded",
        "quota exceeded",
        "quota exhausted",
        "billing_hard_limit",
    )
    return _contains_any(str(detail).casefold(), markers)


def _google_status_code(exc: Exception) -> int | None:
    code = getattr(exc, "code", None)
    if isinstance(code, int):
        return code
    response = getattr(exc, "response", None)
    response_code = getattr(response, "status_code", None)
    if isinstance(response_code, int):
        return response_code
    names = {
        "unauthenticated": 401,
        "permissiondenied": 403,
        "notfound": 404,
        "resourceexhausted": 429,
        "deadlineexceeded": 408,
    }
    return names.get(type(exc).__name__.casefold())


def _contains_any(value: str, markers: tuple[str, ...]) -> bool:
    return any(marker in value for marker in markers)


def _disable(code: ErrorCode, reason: str) -> LlmFailureDecision:
    return LlmFailureDecision(LlmFailureAction.DISABLE_AND_ROTATE, code, reason)


def _fail(code: ErrorCode, reason: str) -> LlmFailureDecision:
    return LlmFailureDecision(LlmFailureAction.FAIL, code, reason)
