"""Factory multi-provider gateway và process-lifetime shared state."""

from dataclasses import dataclass
from functools import lru_cache

from config import Settings, get_settings
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.llm.api_credential import ApiCredential
from src.infrastructure.llm.credential_pool import CredentialPool
from src.infrastructure.llm.lazy_chat_model import StructuredChatModel
from src.infrastructure.llm.llm_gateway import (
    LlmGateway,
    LlmGatewayResources,
    ProviderGatewayRoute,
)
from src.infrastructure.llm.provider_health import ProviderHealthRegistry
from src.infrastructure.llm.provider_registry import (
    ChatModelProviderRegistry,
    create_default_provider_registry,
)
from src.infrastructure.llm.provider_types import LlmProvider
from src.infrastructure.llm.runtime_configuration import (
    OPENROUTER_BASE_URL,
    LlmRuntimeConfiguration,
    resolve_provider_config,
    resolve_runtime_configuration,
)

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class GatewaySharedState:
    """Credential pools và provider health dùng chung giữa model profiles."""

    pools: dict[LlmProvider, CredentialPool]
    health: ProviderHealthRegistry


def build_chat_model(
    settings: Settings | None = None,
    registry: ChatModelProviderRegistry | None = None,
    shared_state: GatewaySharedState | None = None,
) -> StructuredChatModel:
    """Dựng multi-provider gateway từ typed configuration."""
    runtime = resolve_runtime_configuration(settings or get_settings())
    provider_registry = registry or create_default_provider_registry()
    _validate_registry(runtime, provider_registry)
    state = shared_state or _build_shared_state(runtime)
    return _build_rotating_model(runtime, provider_registry, state)


@lru_cache
def get_cached_api_key_pool() -> GatewaySharedState:
    """Compatibility name cho shared multi-provider credential/health state."""
    runtime = resolve_runtime_configuration(get_settings())
    return _build_shared_state(runtime)


@lru_cache
def get_cached_chat_model() -> StructuredChatModel:
    """Khởi tạo default gateway một lần theo process."""
    return build_chat_model(shared_state=get_cached_api_key_pool())


@lru_cache
def get_cached_summary_chat_model() -> StructuredChatModel:
    """Khởi tạo summary gateway và chia sẻ credential/provider health state."""
    settings = get_settings()
    overrides = (
        settings.conversation_summary_model_name,
        settings.conversation_summary_temperature,
        settings.conversation_summary_max_output_tokens,
    )
    runtime = resolve_runtime_configuration(settings, overrides)
    registry = create_default_provider_registry()
    _validate_registry(runtime, registry)
    return _build_rotating_model(runtime, registry, get_cached_api_key_pool())


def validate_llm_gateway_startup(settings: Settings | None = None) -> None:
    """Fail-fast toàn bộ configuration/adapter tại application startup."""
    configured = settings or get_settings()
    runtime = resolve_runtime_configuration(configured)
    registry = create_default_provider_registry()
    _validate_registry(runtime, registry)
    _build_rotating_model(runtime, registry, _build_shared_state(runtime))


def _build_rotating_model(
    runtime: LlmRuntimeConfiguration,
    registry: ChatModelProviderRegistry,
    shared_state: GatewaySharedState,
) -> StructuredChatModel:
    """Compatibility hook dựng gateway routes cho một model profile."""
    try:
        routes = tuple(_build_route(candidate, runtime, registry, shared_state) for candidate in runtime.candidates)
        return LlmGateway(LlmGatewayResources(routes, shared_state.health))
    except InfrastructureException:
        raise
    except Exception as exc:
        logger.exception("Không thể khởi tạo LLM Gateway.")
        raise InfrastructureException(
            ErrorCode.LLM_ERROR,
            "Không thể khởi tạo LLM Gateway.",
        ) from exc


def _build_route(
    candidate: object,
    runtime: LlmRuntimeConfiguration,
    registry: ChatModelProviderRegistry,
    shared_state: GatewaySharedState,
) -> ProviderGatewayRoute:
    configuration = candidate
    provider = configuration.provider
    options = (runtime.temperature, runtime.max_tokens, runtime.timeout_seconds)
    clients = {
        _key_id(provider, index): registry.build(configuration.for_key(key, options))
        for index, key in enumerate(configuration.api_keys, start=1)
    }
    return ProviderGatewayRoute(configuration, clients, shared_state.pools[provider])


def _build_shared_state(runtime: LlmRuntimeConfiguration) -> GatewaySharedState:
    pools = {candidate.provider: _build_pool(candidate, runtime) for candidate in runtime.candidates}
    providers = tuple(candidate.provider for candidate in runtime.candidates)
    health_policy = (runtime.policy.provider_failure_threshold, runtime.policy.provider_cooldown_seconds)
    return GatewaySharedState(pools, ProviderHealthRegistry(providers, health_policy))


def _build_pool(candidate: object, runtime: LlmRuntimeConfiguration) -> CredentialPool:
    credentials = tuple(
        ApiCredential(_key_id(candidate.provider, index), candidate.provider, key)
        for index, key in enumerate(candidate.api_keys, start=1)
    )
    return CredentialPool(credentials, runtime.policy.credential_cooldown_seconds)


def _validate_registry(runtime: LlmRuntimeConfiguration, registry: ChatModelProviderRegistry) -> None:
    missing = [
        candidate.provider.value
        for candidate in runtime.candidates
        if candidate.provider.value.casefold() not in registry.supported_providers
    ]
    if missing:
        raise InfrastructureException(ErrorCode.LLM_ERROR, "LLM provider chưa được đăng ký.")


def _key_id(provider: LlmProvider, index: int) -> str:
    return f"{provider.value.casefold()}_{index:02d}"


__all__ = [
    "OPENROUTER_BASE_URL",
    "build_chat_model",
    "get_cached_api_key_pool",
    "get_cached_chat_model",
    "get_cached_summary_chat_model",
    "resolve_provider_config",
    "validate_llm_gateway_startup",
]

