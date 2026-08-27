"""Multi-provider LLM Gateway với credential rotation và provider fallback."""

from dataclasses import dataclass
from time import perf_counter

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.llm.credential_pool import CredentialPool
from src.infrastructure.llm.exception_translator import translate_llm_failure
from src.infrastructure.llm.failure_classifier import LlmFailureAction, LlmFailureClassifier
from src.infrastructure.llm.lazy_chat_model import StructuredModel
from src.infrastructure.llm.provider_health import ProviderHealthRegistry
from src.infrastructure.llm.runtime_configuration import ProviderRuntimeConfiguration

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class ProviderGatewayRoute:
    """Một provider route cùng client cache và credential pool."""

    configuration: ProviderRuntimeConfiguration
    clients: dict[str, BaseChatModel]
    credential_pool: CredentialPool


@dataclass(frozen=True, slots=True)
class LlmGatewayResources:
    """Process resources dùng bởi một logical model profile."""

    routes: tuple[ProviderGatewayRoute, ...]
    health: ProviderHealthRegistry


class LlmGateway:
    """Gateway provider-neutral giữ contract structured output của Agent."""

    def __init__(self, resources: LlmGatewayResources) -> None:
        self._resources = resources

    def with_structured_output(
        self,
        schema: type[BaseModel],
        *,
        include_raw: bool = False,
    ) -> StructuredModel:
        """Bind output schema cho một logical multi-provider invocation."""
        return GatewayStructuredModel(self._resources, schema, include_raw)


class GatewayStructuredModel:
    """Điều phối provider routing và credential rotation tách biệt."""

    def __init__(
        self,
        resources: LlmGatewayResources,
        schema: type[BaseModel],
        include_raw: bool,
    ) -> None:
        self._resources = resources
        self._schema = schema
        self._include_raw = include_raw
        self._classifier = LlmFailureClassifier()

    async def ainvoke(self, messages: list[object]) -> BaseModel | dict[str, object]:
        """Duyệt ordered providers và chỉ fallback với lỗi hạ tầng phù hợp."""
        last_exc: Exception | None = None
        for route_index, route in enumerate(self._resources.routes):
            provider = route.configuration.provider
            if not await self._resources.health.is_available(provider):
                self._log_fallback(route, route_index, "provider_cooldown")
                continue
            result, last_exc = await self._invoke_provider(route, messages)
            if result is not None:
                return result
            self._log_fallback(route, route_index, "provider_unavailable")
        self._raise_exhausted(last_exc)

    async def _invoke_provider(
        self,
        route: ProviderGatewayRoute,
        messages: list[object],
    ) -> tuple[BaseModel | dict[str, object] | None, Exception | None]:
        attempted: set[str] = set()
        while len(attempted) < route.credential_pool.configured_count:
            lease = await route.credential_pool.acquire(frozenset(attempted))
            if lease is None:
                break
            attempted.add(lease.key_id)
            self._log_selected(route, lease.key_id, len(attempted))
            try:
                result = await self._invoke_client(route.clients[lease.key_id], messages)
            except InfrastructureException:
                raise
            except Exception as exc:
                should_fallback = await self._handle_failure(route, lease.key_id, exc)
                if should_fallback:
                    return None, exc
                continue
            await route.credential_pool.mark_succeeded(lease.key_id)
            await self._resources.health.mark_succeeded(route.configuration.provider)
            return result, None
        return None, None

    async def _invoke_client(
        self,
        client: BaseChatModel,
        messages: list[object],
    ) -> BaseModel | dict[str, object]:
        started = perf_counter()
        structured = (
            client.with_structured_output(self._schema, include_raw=True)
            if self._include_raw
            else client.with_structured_output(self._schema)
        )
        result = await structured.ainvoke(messages)
        logger.info(
            "LLM call completed.",
            extra={"event": "llm_call_completed", "latency_ms": (perf_counter() - started) * 1000},
        )
        return result

    async def _handle_failure(
        self,
        route: ProviderGatewayRoute,
        key_id: str,
        exc: Exception,
    ) -> bool:
        decision = self._classifier.classify(exc)
        self._log_failure(route, key_id, decision.reason)
        if decision.action is LlmFailureAction.FAIL:
            raise translate_llm_failure(decision) from exc
        if decision.action is LlmFailureAction.ROTATE:
            await route.credential_pool.mark_rate_limited(key_id)
            self._log_rotated(route, key_id, decision.reason)
            return False
        if decision.action is LlmFailureAction.DISABLE_AND_ROTATE:
            await route.credential_pool.disable(key_id)
            self._log_rotated(route, key_id, decision.reason)
            return False
        cooled = await self._resources.health.mark_failed(route.configuration.provider)
        if cooled:
            self._log_provider_cooldown(route, decision.reason)
        return True

    def _log_selected(self, route: ProviderGatewayRoute, key_id: str, attempt: int) -> None:
        metadata = self._metadata(route) | {"key_id": key_id, "attempt": attempt}
        logger.info("LLM provider selected.", extra={"event": "llm_provider_selected"} | metadata)
        logger.info("LLM model selected.", extra={"event": "llm_model_selected"} | metadata)

    def _log_rotated(self, route: ProviderGatewayRoute, key_id: str, reason: str) -> None:
        metadata = self._metadata(route) | {"key_id": key_id, "reason": reason}
        logger.warning("LLM key rotated.", extra={"event": "llm_key_rotated"} | metadata)

    def _log_fallback(self, route: ProviderGatewayRoute, index: int, reason: str) -> None:
        metadata = self._metadata(route) | {"provider_index": index, "reason": reason}
        logger.warning("LLM provider fallback.", extra={"event": "llm_provider_fallback"} | metadata)

    def _log_failure(self, route: ProviderGatewayRoute, key_id: str, reason: str) -> None:
        metadata = self._metadata(route) | {"key_id": key_id, "reason": reason}
        logger.warning("LLM call failed.", extra={"event": "llm_call_failed"} | metadata)

    def _log_provider_cooldown(self, route: ProviderGatewayRoute, reason: str) -> None:
        metadata = self._metadata(route) | {"reason": reason}
        logger.warning("LLM provider cooldown.", extra={"event": "llm_provider_cooldown"} | metadata)

    @staticmethod
    def _metadata(route: ProviderGatewayRoute) -> dict[str, object]:
        return {
            "provider": route.configuration.provider.value,
            "model": route.configuration.model_name,
        }

    @staticmethod
    def _raise_exhausted(last_exc: Exception | None) -> None:
        error = InfrastructureException(
            ErrorCode.LLM_CREDENTIALS_EXHAUSTED,
            "Không còn LLM provider hoặc credential khả dụng trong process.",
        )
        raise error from last_exc
