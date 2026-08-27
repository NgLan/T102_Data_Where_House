"""Unit test classifier dùng type và structured status của provider SDK."""

import httpx
import pytest
from openai import AuthenticationError, RateLimitError
from src.common.exceptions.error_codes import ErrorCode
from src.infrastructure.llm.failure_classifier import LlmFailureAction, LlmFailureClassifier


def _response(status: int) -> httpx.Response:
    return httpx.Response(status, request=httpx.Request("POST", "https://provider.invalid"))


def _google_rate_limit_error() -> Exception:
    try:
        from google.genai.errors import ClientError

        return ClientError(
            429,
            {"error": {"status": "RESOURCE_EXHAUSTED", "message": "request rate reached"}},
        )
    except ImportError:
        from google.api_core.exceptions import ResourceExhausted

        return ResourceExhausted("request rate reached")


class AnthropicUnavailableError(Exception):
    """Fake typed Anthropic SDK outage."""

    status_code = 503


AnthropicUnavailableError.__module__ = "anthropic._exceptions"


def test_openai_authentication_disables_key() -> None:
    exc = AuthenticationError("raw", response=_response(401), body={})

    decision = LlmFailureClassifier().classify(exc)

    assert decision.action is LlmFailureAction.DISABLE_AND_ROTATE
    assert decision.code is ErrorCode.LLM_AUTHENTICATION_ERROR


@pytest.mark.parametrize(
    ("body", "action", "code"),
    [
        (
            {"error": {"code": "insufficient_quota"}},
            LlmFailureAction.DISABLE_AND_ROTATE,
            ErrorCode.LLM_QUOTA_EXCEEDED,
        ),
        ({"error": {"code": "rate_limit"}}, LlmFailureAction.ROTATE, ErrorCode.LLM_RATE_LIMIT_ERROR),
    ],
)
def test_openai_rate_limit_distinguishes_quota(
    body: object, action: LlmFailureAction, code: ErrorCode
) -> None:
    exc = RateLimitError("raw", response=_response(429), body=body)

    decision = LlmFailureClassifier().classify(exc)

    assert decision.action is action
    assert decision.code is code


def test_google_resource_exhausted_rotates_without_permanent_disable() -> None:
    decision = LlmFailureClassifier().classify(_google_rate_limit_error())

    assert decision.action is LlmFailureAction.ROTATE
    assert decision.code is ErrorCode.LLM_RATE_LIMIT_ERROR


def test_anthropic_5xx_falls_back_provider() -> None:
    decision = LlmFailureClassifier().classify(AnthropicUnavailableError())

    assert decision.action is LlmFailureAction.FALLBACK_PROVIDER
    assert decision.code is ErrorCode.LLM_ERROR


@pytest.mark.parametrize(
    ("exc", "code"),
    [
        (ValueError("invalid request"), ErrorCode.LLM_ERROR),
        (TimeoutError("secret detail"), ErrorCode.LLM_TIMEOUT_ERROR),
        (ValueError("validation error"), ErrorCode.LLM_ERROR),
    ],
)
def test_non_key_failure_does_not_rotate(exc: Exception, code: ErrorCode) -> None:
    decision = LlmFailureClassifier().classify(exc)

    expected = (
        LlmFailureAction.FALLBACK_PROVIDER
        if isinstance(exc, TimeoutError)
        else LlmFailureAction.FAIL
    )
    assert decision.action is expected
    assert decision.code is code
