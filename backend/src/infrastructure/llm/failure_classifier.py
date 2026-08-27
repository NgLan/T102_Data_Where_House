"""Phân loại lỗi LLM thành quyết định failover không làm lộ provider detail."""

from dataclasses import dataclass
from enum import StrEnum

import httpx
from pydantic import ValidationError
from src.common.exceptions.error_codes import ErrorCode
from src.infrastructure.llm.failure_details import (
    contains_any,
    contains_quota_marker,
    google_status_code,
)


class LlmFailureAction(StrEnum):
    """Hành động hạ tầng sau khi phân loại lỗi provider."""

    FAIL = "FAIL"
    ROTATE = "ROTATE"
    DISABLE_AND_ROTATE = "DISABLE_AND_ROTATE"
    FALLBACK_PROVIDER = "FALLBACK_PROVIDER"


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
        if _sdk_type(exc, "openai", ("AuthenticationError", "PermissionDeniedError")):
            return _disable(ErrorCode.LLM_AUTHENTICATION_ERROR, "authentication")
        if _sdk_type(exc, "openai", ("RateLimitError",)):
            return self._rate_limit_decision(getattr(exc, "body", None))
        if _sdk_type(exc, "openai", ("NotFoundError",)):
            return _fail(ErrorCode.LLM_MODEL_NOT_FOUND, "model_not_found")
        if _sdk_module(exc, "openai") and _status_code(exc) >= 500:
            return _fallback(ErrorCode.LLM_ERROR, "provider_unavailable")
        if _sdk_module(exc, "google") or _sdk_module(exc, "anthropic"):
            return self._provider_status_decision(exc)
        if _sdk_type(exc, "openai", ("APITimeoutError", "APIConnectionError")):
            return _fallback(ErrorCode.LLM_TIMEOUT_ERROR, "transient_network")
        if isinstance(exc, httpx.TransportError):
            return _fallback(ErrorCode.LLM_TIMEOUT_ERROR, "transient_network")
        if isinstance(exc, (TimeoutError, ConnectionError)):
            return _fallback(ErrorCode.LLM_TIMEOUT_ERROR, "transient_network")
        if isinstance(exc, ValidationError) or "outputparser" in type(exc).__name__.casefold():
            return _fail(ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR, "structured_output")
        return self._fallback_decision(exc)

    def _provider_status_decision(self, exc: Exception) -> LlmFailureDecision:
        status_code = _status_code(exc) or google_status_code(exc)
        if status_code in {401, 403}:
            return _disable(ErrorCode.LLM_AUTHENTICATION_ERROR, "authentication")
        if status_code == 404:
            return _fail(ErrorCode.LLM_MODEL_NOT_FOUND, "model_not_found")
        if status_code == 429:
            return self._rate_limit_decision(getattr(exc, "details", exc))
        if status_code == 408:
            return _fallback(ErrorCode.LLM_TIMEOUT_ERROR, "transient_network")
        if status_code is not None and status_code >= 500:
            return _fallback(ErrorCode.LLM_ERROR, "provider_unavailable")
        return _fail(ErrorCode.LLM_ERROR, "provider_error")

    def _rate_limit_decision(self, detail: object) -> LlmFailureDecision:
        if contains_quota_marker(detail):
            return _disable(ErrorCode.LLM_QUOTA_EXCEEDED, "quota_exhausted")
        return LlmFailureDecision(LlmFailureAction.ROTATE, ErrorCode.LLM_RATE_LIMIT_ERROR, "rate_limit")

    def _fallback_decision(self, exc: Exception) -> LlmFailureDecision:
        message = str(exc).casefold()
        if contains_any(message, ("invalid api key", "api key expired", "revoked", "unauthorized")):
            return _disable(ErrorCode.LLM_AUTHENTICATION_ERROR, "authentication")
        if contains_quota_marker(message):
            return _disable(ErrorCode.LLM_QUOTA_EXCEEDED, "quota_exhausted")
        if contains_any(message, ("rate limit", "resource_exhausted", "resourceexhausted")):
            return LlmFailureDecision(LlmFailureAction.ROTATE, ErrorCode.LLM_RATE_LIMIT_ERROR, "rate_limit")
        if contains_any(message, ("404", "not found", "not_found")):
            return _fail(ErrorCode.LLM_MODEL_NOT_FOUND, "model_not_found")
        if contains_any(message, ("timeout", "timed out", "connection reset")):
            return _fallback(ErrorCode.LLM_TIMEOUT_ERROR, "transient_network")
        if contains_any(message, ("service unavailable", "server error", "internal error")):
            return _fallback(ErrorCode.LLM_ERROR, "provider_unavailable")
        return _fail(ErrorCode.LLM_ERROR, "provider_error")


def _disable(code: ErrorCode, reason: str) -> LlmFailureDecision:
    return LlmFailureDecision(LlmFailureAction.DISABLE_AND_ROTATE, code, reason)


def _fail(code: ErrorCode, reason: str) -> LlmFailureDecision:
    return LlmFailureDecision(LlmFailureAction.FAIL, code, reason)


def _fallback(code: ErrorCode, reason: str) -> LlmFailureDecision:
    return LlmFailureDecision(LlmFailureAction.FALLBACK_PROVIDER, code, reason)


def _sdk_module(exc: Exception, provider: str) -> bool:
    module = type(exc).__module__.casefold()
    return module == provider or module.startswith(f"{provider}.")


def _sdk_type(exc: Exception, provider: str, names: tuple[str, ...]) -> bool:
    return _sdk_module(exc, provider) and type(exc).__name__ in names


def _status_code(exc: Exception) -> int:
    value = getattr(exc, "status_code", 0)
    return value if isinstance(value, int) else 0
