"""Factory provider-neutral và process-lifetime cho các Agent."""

from functools import lru_cache

from config import Settings, get_settings
from pydantic import SecretStr
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.llm.api_key_pool import LlmApiKeyPool
from src.infrastructure.llm.lazy_chat_model import StructuredChatModel
from src.infrastructure.llm.provider_registry import (
    ChatModelProviderRegistry,
    create_default_provider_registry,
)
from src.infrastructure.llm.rotating_chat_model import RotatingChatModel, RotatingChatModelResources
from src.infrastructure.llm.runtime_configuration import (
    OPENROUTER_BASE_URL,
    LlmRuntimeConfiguration,
    is_local_endpoint,
    resolve_provider_config,
    resolve_runtime_configuration,
)

logger = get_logger(__name__)
LOCAL_CLIENT_KEY = SecretStr("local")


def build_chat_model(
    settings: Settings | None = None,
    registry: ChatModelProviderRegistry | None = None,
    key_pool: LlmApiKeyPool | None = None,
) -> StructuredChatModel:
    """Dựng rotating chat model từ cấu hình hoặc báo lỗi hạ tầng an toàn."""
    runtime = resolve_runtime_configuration(settings or get_settings())
    pool = key_pool or LlmApiKeyPool(_client_keys(runtime))
    return _build_rotating_model(runtime, registry or create_default_provider_registry(), pool)


@lru_cache
def get_cached_api_key_pool() -> LlmApiKeyPool:
    """Tạo một key pool chia sẻ giữa mọi logical model trong process."""
    runtime = resolve_runtime_configuration(get_settings())
    return LlmApiKeyPool(_client_keys(runtime))


@lru_cache
def get_cached_chat_model() -> StructuredChatModel:
    """Khởi tạo default model một lần và dùng shared key state."""
    return build_chat_model(key_pool=get_cached_api_key_pool())


@lru_cache
def get_cached_summary_chat_model() -> StructuredChatModel:
    """Khởi tạo summary model riêng nhưng chia sẻ key state với default model."""
    settings = get_settings()
    overrides = (
        settings.conversation_summary_model_name or settings.model_name,
        settings.conversation_summary_temperature,
        settings.conversation_summary_max_output_tokens,
    )
    runtime = resolve_runtime_configuration(settings, overrides)
    return _build_rotating_model(runtime, create_default_provider_registry(), get_cached_api_key_pool())


def _build_rotating_model(
    runtime: LlmRuntimeConfiguration,
    registry: ChatModelProviderRegistry,
    key_pool: LlmApiKeyPool,
) -> StructuredChatModel:
    """Dựng và reuse đúng một provider client cho mỗi key slot."""
    try:
        clients = tuple(registry.build(runtime.for_key(key)) for key in _client_keys(runtime))
        resources = RotatingChatModelResources(clients, key_pool, runtime.provider)
        return RotatingChatModel(resources)
    except InfrastructureException:
        raise
    except Exception as exc:
        logger.error("Không thể khởi tạo mô hình ngôn ngữ.")
        raise InfrastructureException(
            ErrorCode.LLM_ERROR, "Không thể khởi tạo mô hình ngôn ngữ."
        ) from exc


def _client_keys(runtime: LlmRuntimeConfiguration) -> tuple[SecretStr, ...]:
    if runtime.api_keys:
        return runtime.api_keys
    if is_local_endpoint(runtime.base_url):
        return (LOCAL_CLIENT_KEY,)
    raise InfrastructureException(ErrorCode.LLM_ERROR, "Chưa cấu hình API key cho LLM.")


__all__ = [
    "build_chat_model",
    "get_cached_api_key_pool",
    "get_cached_chat_model",
    "get_cached_summary_chat_model",
    "OPENROUTER_BASE_URL",
    "resolve_provider_config",
]
