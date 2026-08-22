"""Factory provider-neutral dùng chung cho các Agent."""

from functools import lru_cache

from config import Settings, get_settings
from langchain_core.language_models import BaseChatModel
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.llm.provider_registry import (
    ChatModelConfiguration,
    ChatModelProviderRegistry,
    create_default_provider_registry,
)

logger = get_logger(__name__)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def build_chat_model(
    settings: Settings | None = None,
    registry: ChatModelProviderRegistry | None = None,
) -> BaseChatModel:
    """Dựng chat model theo provider được cấu hình.

    Raises:
        InfrastructureException: Khi thiếu key hoặc provider khởi tạo thất bại.
    """
    app_settings = settings or get_settings()
    configuration = _configuration(app_settings)
    if not configuration.api_key and not _is_local(configuration.base_url):
        raise InfrastructureException(ErrorCode.LLM_ERROR, "Chưa cấu hình API key cho LLM.")
    try:
        return (registry or create_default_provider_registry()).build(configuration)
    except InfrastructureException:
        raise
    except Exception as exc:
        logger.exception("Khởi tạo chat model thất bại.")
        raise InfrastructureException(
            ErrorCode.LLM_ERROR, "Không thể khởi tạo mô hình ngôn ngữ."
        ) from exc


@lru_cache
def get_cached_chat_model() -> BaseChatModel:
    """Khởi tạo khi Agent dùng lần đầu và cache default model theo process."""
    return build_chat_model()


def resolve_provider_config(api_key: str, base_url: str, model_name: str) -> tuple[str, str]:
    """Giữ tương thích OpenRouter và OpenAI-compatible configuration."""
    resolved_url = base_url.strip().rstrip("/")
    if not resolved_url and api_key.lower().startswith("sk-or-v1-"):
        resolved_url = OPENROUTER_BASE_URL
    resolved_model = model_name.strip()
    openai_prefixes = ("gpt-", "chatgpt-", "o1", "o3", "o4")
    if resolved_url.casefold() == OPENROUTER_BASE_URL.casefold():
        if "/" not in resolved_model and resolved_model.startswith(openai_prefixes):
            resolved_model = f"openai/{resolved_model}"
    return resolved_url, resolved_model


def _configuration(settings: Settings) -> ChatModelConfiguration:
    """Chuẩn hóa config mới và fallback biến môi trường cũ."""
    provider = settings.llm_provider.strip().casefold()
    api_key = settings.llm_api_key.strip()
    if not api_key:
        api_key = settings.google_api_key if provider == "google" else settings.openai_api_key
    base_url = settings.llm_base_url.strip()
    if not base_url and provider != "google":
        base_url = settings.openai_base_url.strip()
    base_url, model_name = resolve_provider_config(api_key, base_url, settings.model_name)
    return ChatModelConfiguration(
        provider,
        model_name,
        api_key,
        base_url,
        settings.llm_temperature,
        settings.agent_max_output_tokens,
        settings.llm_request_timeout_seconds,
    )


def _is_local(base_url: str) -> bool:
    """Nhận diện endpoint local không yêu cầu secret thật."""
    normalized = base_url.casefold()
    return "localhost" in normalized or "127.0.0.1" in normalized
