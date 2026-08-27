"""Chat model proxy thực hiện key failover trong một structured invocation."""

from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.llm.api_key_pool import LlmApiKeyPool, LlmKeyLease
from src.infrastructure.llm.exception_translator import translate_llm_failure
from src.infrastructure.llm.failure_classifier import LlmFailureAction, LlmFailureClassifier, LlmFailureDecision
from src.infrastructure.llm.lazy_chat_model import StructuredModel

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class RotatingChatModelResources:
    """Tài nguyên process-lifetime của một model logical."""

    clients: tuple[BaseChatModel, ...]
    key_pool: LlmApiKeyPool
    provider: str


class RotatingChatModel:
    """Cung cấp contract structured output tương thích Agent hiện tại."""

    def __init__(self, resources: RotatingChatModelResources) -> None:
        self._resources = resources

    def with_structured_output(
        self,
        schema: type[BaseModel],
        *,
        include_raw: bool = False,
    ) -> StructuredModel:
        """Tạo runnable failover cho schema của invocation."""
        return RotatingStructuredModel(self._resources, schema, include_raw)


class RotatingStructuredModel:
    """Thử tối đa một lần trên mỗi configured key slot."""

    def __init__(
        self,
        resources: RotatingChatModelResources,
        schema: type[BaseModel],
        include_raw: bool,
    ) -> None:
        self._resources = resources
        self._schema = schema
        self._include_raw = include_raw
        self._classifier = LlmFailureClassifier()

    async def ainvoke(self, messages: list[object]) -> BaseModel | dict[str, object]:
        """Gọi provider và chuyển slot đối với lỗi key-specific."""
        attempted: set[int] = set()
        last_exc: Exception | None = None
        previous_slot: int | None = None
        while len(attempted) < self._resources.key_pool.configured_key_count:
            lease = await self._resources.key_pool.acquire(frozenset(attempted))
            if lease is None:
                break
            self._log_rotated(previous_slot, lease.slot, len(attempted) + 1)
            attempted.add(lease.slot)
            try:
                result = await self._invoke_client(lease, messages)
            except InfrastructureException:
                raise
            except Exception as exc:
                last_exc, previous_slot = await self._handle_failure(exc, lease, len(attempted))
                continue
            await self._resources.key_pool.mark_succeeded(lease.slot)
            return result
        self._raise_exhausted(last_exc, len(attempted))

    async def _invoke_client(
        self,
        lease: LlmKeyLease,
        messages: list[object],
    ) -> BaseModel | dict[str, object]:
        client = self._resources.clients[lease.slot]
        structured = (
            client.with_structured_output(self._schema, include_raw=True)
            if self._include_raw
            else client.with_structured_output(self._schema)
        )
        return await structured.ainvoke(messages)

    async def _handle_failure(
        self, exc: Exception, lease: LlmKeyLease, attempt: int
    ) -> tuple[Exception, int]:
        decision = self._classifier.classify(exc)
        if decision.action is LlmFailureAction.FAIL:
            raise translate_llm_failure(decision) from exc
        await self._resources.key_pool.mark_failed(
            lease.slot, decision.action is LlmFailureAction.DISABLE_AND_ROTATE
        )
        self._log_rotation(lease.slot, decision, attempt)
        return exc, lease.slot

    def _log_rotation(self, slot: int, decision: LlmFailureDecision, attempt: int) -> None:
        metadata = self._metadata(attempt) | {"from_slot": slot, "reason": decision.reason}
        logger.warning("LLM key rotation started.", extra={"event": "llm_key_rotation_started"} | metadata)
        if decision.action is LlmFailureAction.DISABLE_AND_ROTATE:
            disabled = metadata | {"llm_key_slot": slot}
            logger.warning("LLM key disabled for process.", extra={"event": "llm_key_disabled"} | disabled)

    def _log_rotated(self, previous: int | None, current: int, attempt: int) -> None:
        if previous is None:
            return
        metadata = self._metadata(attempt) | {"from_slot": previous, "to_slot": current}
        logger.info("LLM key rotated.", extra={"event": "llm_key_rotated"} | metadata)

    def _raise_exhausted(self, last_exc: Exception | None, attempt: int) -> None:
        logger.error(
            "LLM key pool exhausted.",
            extra={"event": "llm_key_pool_exhausted"} | self._metadata(attempt),
        )
        error = InfrastructureException(
            ErrorCode.LLM_CREDENTIALS_EXHAUSTED,
            "Không còn LLM credential khả dụng trong process.",
        )
        raise error from last_exc

    def _metadata(self, attempt: int) -> dict[str, object]:
        return {
            "provider": self._resources.provider,
            "attempt": attempt,
            "configured_key_count": self._resources.key_pool.configured_key_count,
        }
