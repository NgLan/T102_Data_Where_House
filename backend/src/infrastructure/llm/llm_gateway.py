"""Multi-provider LLM Gateway với credential rotation và provider fallback."""

from dataclasses import dataclass
from time import perf_counter

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.llm.credential_pool import CredentialPool
from src.infrastructure.llm.gateway_failure_handler import GatewayFailureHandler
from src.infrastructure.llm.gateway_observability import (
    GatewayLogContext,
    log_call_completed,
    log_fallback,
    log_selected,
)
from src.infrastructure.llm.lazy_chat_model import StructuredModel
from src.infrastructure.llm.provider_health import ProviderHealthRegistry
from src.infrastructure.llm.provider_routing_policy import ProviderRoutingPolicy
from src.infrastructure.llm.runtime_configuration import ProviderRuntimeConfiguration
from src.infrastructure.llm.structured_raw_response import extract_metadata


@dataclass(frozen=True, slots=True)
class ProviderGatewayRoute:
    """Một provider route cùng client cache và credential pool."""

    configuration: ProviderRuntimeConfiguration
    clients: dict[str, BaseChatModel]
    credential_pool: CredentialPool


@dataclass(frozen=True, slots=True)
class LlmGatewayResources:
    """Process resources dùng bởi một logical model profile."""

    routing_policy: ProviderRoutingPolicy[ProviderGatewayRoute]
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
        self._failure_handler = GatewayFailureHandler(resources.health)

    async def ainvoke(self, messages: list[object]) -> BaseModel | dict[str, object]:
        """Duyệt ordered providers và chỉ fallback với lỗi hạ tầng phù hợp."""
        last_exc: Exception | None = None
        for route_index, route in enumerate(self._resources.routing_policy.ordered()):
            provider = route.configuration.provider
            if not await self._resources.health.is_available(provider):
                log_fallback(_log_context(route), route_index, "provider_cooldown")
                continue
            result, last_exc = await self._invoke_provider(route, messages)
            if result is not None:
                return result
            log_fallback(_log_context(route), route_index, "provider_unavailable")
        self._raise_exhausted(last_exc)

    async def _invoke_provider(
        self,
        route: ProviderGatewayRoute,
        messages: list[object],
    ) -> tuple[BaseModel | dict[str, object] | None, Exception | None]:
        attempted: set[str] = set()
        provider_exc: Exception | None = None
        while len(attempted) < route.credential_pool.configured_count:
            lease = await route.credential_pool.acquire(frozenset(attempted))
            if lease is None:
                break
            attempted.add(lease.key_id)
            log_selected(_log_context(route), lease.key_id, len(attempted))
            result, provider_exc, fallback = await self._try_credential(route, lease.key_id, messages)
            if result is not None:
                return result, None
            if fallback:
                return None, provider_exc
        return None, provider_exc

    async def _try_credential(
        self,
        route: ProviderGatewayRoute,
        key_id: str,
        messages: list[object],
    ) -> tuple[BaseModel | dict[str, object] | None, Exception | None, bool]:
        try:
            result = await self._invoke_client(route.clients[key_id], messages, _log_context(route))
        except InfrastructureException:
            raise
        except Exception as exc:
            fallback = await self._failure_handler.handle(route, key_id, exc)
            return None, exc, fallback
        await route.credential_pool.mark_succeeded(key_id)
        await self._resources.health.mark_succeeded(route.configuration.provider)
        return result, None, False

    async def _invoke_client(
        self,
        client: BaseChatModel,
        messages: list[object],
        context: GatewayLogContext,
    ) -> BaseModel | dict[str, object]:
        started = perf_counter()
        structured = (
            client.with_structured_output(self._schema, include_raw=True)
            if self._include_raw
            else client.with_structured_output(self._schema)
        )
        result = await structured.ainvoke(messages)
        raw = result.get("raw") if isinstance(result, dict) else result
        log_call_completed(context, extract_metadata(raw), (perf_counter() - started) * 1000)
        return result

    @staticmethod
    def _raise_exhausted(last_exc: Exception | None) -> None:
        error = InfrastructureException(
            ErrorCode.LLM_CREDENTIALS_EXHAUSTED, "Không còn LLM provider hoặc credential khả dụng trong process."
        )
        raise error from last_exc


def _log_context(route: ProviderGatewayRoute) -> GatewayLogContext:
    return GatewayLogContext(route.configuration.provider.value, route.configuration.model_name)
