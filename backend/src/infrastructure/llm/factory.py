"""Factory thuần để dựng multi-provider gateway resources."""

from config import Settings, get_settings
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.llm.gateway_builder import (
    GatewaySharedState,
    build_gateway,
    build_shared_state,
    validate_registry,
)
from src.infrastructure.llm.lazy_chat_model import ILLMGateway
from src.infrastructure.llm.provider_registry import (
    ChatModelProviderRegistry,
    create_default_provider_registry,
)
from src.infrastructure.llm.runtime_configuration import (
    OPENROUTER_BASE_URL,
    LlmRuntimeConfiguration,
    resolve_provider_config,
    resolve_runtime_configuration,
)

logger = get_logger(__name__)


def build_chat_model(
    settings: Settings | None = None,
    registry: ChatModelProviderRegistry | None = None,
    shared_state: GatewaySharedState | None = None,
) -> ILLMGateway:
    """Dựng multi-provider gateway từ typed configuration."""
    runtime = _resolve_runtime(settings or get_settings())
    provider_registry = registry or create_default_provider_registry()
    validate_registry(runtime, provider_registry)
    state = shared_state or build_shared_state(runtime)
    return _build_gateway(runtime, provider_registry, state)


def build_gateway_state(settings: Settings | None = None) -> GatewaySharedState:
    """Dựng shared multi-provider credential/health state."""
    runtime = _resolve_runtime(settings or get_settings())
    return build_shared_state(runtime)


def build_summary_chat_model(
    settings: Settings | None = None,
    registry: ChatModelProviderRegistry | None = None,
    shared_state: GatewaySharedState | None = None,
) -> ILLMGateway:
    """Dựng summary profile gateway trên shared process state."""
    configured = settings or get_settings()
    overrides = (
        configured.conversation_summary_model_name,
        configured.conversation_summary_temperature,
        configured.conversation_summary_max_output_tokens,
    )
    runtime = _resolve_runtime(configured, overrides)
    provider_registry = registry or create_default_provider_registry()
    validate_registry(runtime, provider_registry)
    state = shared_state or build_gateway_state(configured)
    return _build_gateway(runtime, provider_registry, state)


def validate_llm_gateway_startup(settings: Settings | None = None) -> None:
    """Fail-fast toàn bộ configuration/adapter tại application startup."""
    configured = settings or get_settings()
    runtime = _resolve_runtime(configured)
    registry = create_default_provider_registry()
    validate_registry(runtime, registry)
    state = build_shared_state(runtime)
    _build_gateway(runtime, registry, state)
    build_summary_chat_model(configured, registry, state)


def _build_gateway(
    runtime: LlmRuntimeConfiguration,
    registry: ChatModelProviderRegistry,
    shared_state: GatewaySharedState,
) -> ILLMGateway:
    """Compatibility hook dựng gateway routes cho một model profile."""
    try:
        return build_gateway(runtime, registry, shared_state)
    except InfrastructureException:
        raise
    except Exception as exc:
        logger.error("Không thể khởi tạo LLM Gateway.")
        raise InfrastructureException(
            ErrorCode.LLM_ERROR,
            "Không thể khởi tạo LLM Gateway.",
        ) from exc


def _resolve_runtime(
    settings: Settings,
    overrides: tuple[str, float, int] | None = None,
) -> LlmRuntimeConfiguration:
    try:
        return resolve_runtime_configuration(settings, overrides)
    except ValueError as exc:
        raise InfrastructureException(
            ErrorCode.LLM_ERROR,
            "Cấu hình LLM Gateway không hợp lệ.",
        ) from exc


__all__ = [
    "OPENROUTER_BASE_URL",
    "build_chat_model",
    "build_gateway_state",
    "build_summary_chat_model",
    "resolve_provider_config",
    "validate_llm_gateway_startup",
]
