"""Structured observability events của LLM Gateway."""

from dataclasses import dataclass

from src.common.logging import get_logger
from src.infrastructure.llm.structured_output_models import StructuredInvocationMetadata

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class GatewayLogContext:
    """Route metadata an toàn, không chứa credential secret."""

    provider: str
    model: str

    def metadata(self) -> dict[str, object]:
        """Trả structured fields dùng chung."""
        return {"provider": self.provider, "model": self.model}


def log_selected(context: GatewayLogContext, key_id: str, attempt: int) -> None:
    """Ghi nhận provider/model/anonymous key đã chọn."""
    metadata = context.metadata() | {"key_id": key_id, "attempt": attempt}
    logger.info("LLM provider selected.", extra={"event": "llm_provider_selected"} | metadata)
    logger.info("LLM model selected.", extra={"event": "llm_model_selected"} | metadata)


def log_rotated(context: GatewayLogContext, key_id: str, reason: str) -> None:
    """Ghi nhận credential rotation an toàn."""
    metadata = context.metadata() | {"key_id": key_id, "reason": reason}
    logger.warning("LLM key rotated.", extra={"event": "llm_key_rotated"} | metadata)


def log_fallback(context: GatewayLogContext, index: int, reason: str) -> None:
    """Ghi nhận chuyển sang provider candidate kế tiếp."""
    metadata = context.metadata() | {"provider_index": index, "reason": reason}
    logger.warning("LLM provider fallback.", extra={"event": "llm_provider_fallback"} | metadata)


def log_failure(context: GatewayLogContext, key_id: str, reason: str) -> None:
    """Ghi nhận safe failure category, không ghi raw exception."""
    metadata = context.metadata() | {"key_id": key_id, "reason": reason}
    logger.warning("LLM call failed.", extra={"event": "llm_call_failed"} | metadata)


def log_provider_cooldown(context: GatewayLogContext, reason: str) -> None:
    """Ghi nhận provider chuyển cooldown."""
    metadata = context.metadata() | {"reason": reason}
    logger.warning("LLM provider cooldown.", extra={"event": "llm_provider_cooldown"} | metadata)


def log_call_completed(
    context: GatewayLogContext,
    response: StructuredInvocationMetadata,
    latency_ms: float,
) -> None:
    """Ghi nhận latency của network invocation thành công."""
    metadata = context.metadata() | {
        "latency_ms": latency_ms,
        "finish_reason": response.finish_reason,
        "usage": {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "total": response.total_tokens,
        },
    }
    logger.info(
        "LLM call completed.",
        extra={"event": "llm_call_completed"} | metadata,
    )
