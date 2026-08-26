"""Chuẩn hóa cấu hình runtime cho một provider LLM."""

from dataclasses import dataclass

from config import Settings
from pydantic import SecretStr
from src.infrastructure.llm.provider_registry import ChatModelConfiguration

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


@dataclass(frozen=True, slots=True)
class LlmRuntimeConfiguration:
    """Cấu hình dùng chung để dựng một client cho mỗi key."""

    provider: str
    model_name: str
    api_keys: tuple[SecretStr, ...]
    base_url: str
    temperature: float
    max_tokens: int
    timeout_seconds: float

    def for_key(self, key: SecretStr) -> ChatModelConfiguration:
        """Tạo cấu hình client cho đúng một secret slot."""
        return ChatModelConfiguration(
            self.provider,
            self.model_name,
            key,
            self.base_url,
            self.temperature,
            self.max_tokens,
            self.timeout_seconds,
        )


def resolve_runtime_configuration(
    settings: Settings,
    overrides: tuple[str, float, int] | None = None,
) -> LlmRuntimeConfiguration:
    """Resolve provider, key list và model parameters theo migration precedence."""
    provider = settings.llm_provider.strip().casefold()
    keys = effective_api_keys(settings)
    base_url = _base_url(settings, provider)
    model_name, temperature, max_tokens = overrides or _default_model_parameters(settings)
    first_key = keys[0].get_secret_value() if keys else ""
    base_url, model_name = resolve_provider_config(first_key, base_url, model_name)
    return LlmRuntimeConfiguration(
        provider,
        model_name,
        keys,
        base_url,
        temperature,
        max_tokens,
        settings.llm_request_timeout_seconds,
    )


def effective_api_keys(settings: Settings) -> tuple[SecretStr, ...]:
    """Ưu tiên key list mới, sau đó fallback mềm về biến đơn cũ."""
    if settings.llm_api_keys is not None:
        return settings.llm_api_keys
    provider = settings.llm_provider.strip().casefold()
    legacy = settings.llm_api_key.strip()
    if not legacy:
        legacy = settings.google_api_key if provider == "google" else settings.openai_api_key
    return (SecretStr(legacy.strip()),) if legacy.strip() else ()


def has_llm_configuration(settings: Settings) -> bool:
    """Kiểm tra cloud key hoặc local OpenAI-compatible endpoint."""
    runtime = resolve_runtime_configuration(settings)
    return bool(runtime.api_keys) or is_local_endpoint(runtime.base_url)


def resolve_provider_config(api_key: str, base_url: str, model_name: str) -> tuple[str, str]:
    """Giữ tương thích OpenRouter và OpenAI-compatible configuration."""
    resolved_url = base_url.strip().rstrip("/")
    if not resolved_url and api_key.casefold().startswith("sk-or-v1-"):
        resolved_url = OPENROUTER_BASE_URL
    resolved_model = model_name.strip()
    openai_prefixes = ("gpt-", "chatgpt-", "o1", "o3", "o4")
    if resolved_url.casefold() == OPENROUTER_BASE_URL.casefold():
        if "/" not in resolved_model and resolved_model.startswith(openai_prefixes):
            resolved_model = f"openai/{resolved_model}"
    return resolved_url, resolved_model


def is_local_endpoint(base_url: str) -> bool:
    """Nhận diện endpoint local không yêu cầu secret thật."""
    normalized = base_url.casefold()
    return "localhost" in normalized or "127.0.0.1" in normalized


def _base_url(settings: Settings, provider: str) -> str:
    configured = settings.llm_base_url.strip()
    if not configured and provider != "google":
        configured = settings.openai_base_url.strip()
    return configured


def _default_model_parameters(settings: Settings) -> tuple[str, float, int]:
    return settings.model_name, settings.llm_temperature, settings.agent_max_output_tokens
