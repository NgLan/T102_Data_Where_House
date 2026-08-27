"""Dựng gateway routes và process-shared provider resources."""

from dataclasses import dataclass

from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.llm.api_credential import ApiCredential
from src.infrastructure.llm.credential_pool import CredentialPool
from src.infrastructure.llm.lazy_chat_model import ILLMGateway
from src.infrastructure.llm.llm_gateway import (
    LlmGateway,
    LlmGatewayResources,
    ProviderGatewayRoute,
)
from src.infrastructure.llm.provider_health import ProviderHealthRegistry
from src.infrastructure.llm.provider_registry import ChatModelProviderRegistry
from src.infrastructure.llm.provider_routing_policy import ProviderRoutingPolicy
from src.infrastructure.llm.provider_types import LlmProvider
from src.infrastructure.llm.runtime_configuration import (
    LlmRuntimeConfiguration,
    ProviderRuntimeConfiguration,
)


@dataclass(frozen=True, slots=True)
class GatewaySharedState:
    """Credential pools và provider health dùng chung giữa model profiles."""

    pools: dict[LlmProvider, CredentialPool]
    health: ProviderHealthRegistry


@dataclass(frozen=True, slots=True)
class _GatewayBuildContext:
    runtime: LlmRuntimeConfiguration
    registry: ChatModelProviderRegistry
    shared_state: GatewaySharedState


def build_gateway(
    runtime: LlmRuntimeConfiguration,
    registry: ChatModelProviderRegistry,
    shared_state: GatewaySharedState,
) -> ILLMGateway:
    """Dựng client cache và ordered routes cho một model profile."""
    context = _GatewayBuildContext(runtime, registry, shared_state)
    routes = tuple(_build_route(candidate, context) for candidate in runtime.candidates)
    return LlmGateway(LlmGatewayResources(ProviderRoutingPolicy(routes), shared_state.health))


def build_shared_state(runtime: LlmRuntimeConfiguration) -> GatewaySharedState:
    """Dựng provider-scoped pools và health registry."""
    pools = {candidate.provider: _build_pool(candidate, runtime) for candidate in runtime.candidates}
    providers = tuple(candidate.provider for candidate in runtime.candidates)
    policy = (runtime.policy.provider_failure_threshold, runtime.policy.provider_cooldown_seconds)
    return GatewaySharedState(pools, ProviderHealthRegistry(providers, policy))


def validate_registry(runtime: LlmRuntimeConfiguration, registry: ChatModelProviderRegistry) -> None:
    """Fail-fast khi ordered candidate chưa có provider adapter."""
    missing = [
        candidate.provider.value
        for candidate in runtime.candidates
        if candidate.provider.value.casefold() not in registry.supported_providers
    ]
    if missing:
        raise InfrastructureException(ErrorCode.LLM_ERROR, "LLM provider chưa được đăng ký.")


def _build_route(
    candidate: ProviderRuntimeConfiguration,
    context: _GatewayBuildContext,
) -> ProviderGatewayRoute:
    runtime = context.runtime
    options = (runtime.temperature, runtime.max_tokens, runtime.timeout_seconds)
    clients = {
        _key_id(candidate.provider, index): context.registry.build(candidate.for_key(key, options))
        for index, key in enumerate(candidate.api_keys, start=1)
    }
    pool = context.shared_state.pools[candidate.provider]
    return ProviderGatewayRoute(candidate, clients, pool)


def _build_pool(
    candidate: ProviderRuntimeConfiguration,
    runtime: LlmRuntimeConfiguration,
) -> CredentialPool:
    credentials = tuple(
        ApiCredential(_key_id(candidate.provider, index), candidate.provider, key)
        for index, key in enumerate(candidate.api_keys, start=1)
    )
    return CredentialPool(credentials, runtime.policy.credential_cooldown_seconds)


def _key_id(provider: LlmProvider, index: int) -> str:
    return f"{provider.value.casefold()}_{index:02d}"
