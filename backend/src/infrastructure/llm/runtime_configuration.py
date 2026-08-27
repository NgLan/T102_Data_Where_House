"""Resolve typed multi-provider LLM runtime configuration."""

from dataclasses import dataclass
from typing import Literal

from config import Settings
from pydantic import SecretStr
from src.infrastructure.llm.credential_detector import (
    CredentialProviderDetector,
    create_default_credential_detector,
)
from src.infrastructure.llm.provider_registry_types import ChatModelConfiguration
from src.infrastructure.llm.provider_types import LlmPolicyConfiguration, LlmProvider

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
ModelProfile = Literal["default", "summary"]


@dataclass(frozen=True, slots=True)
class ProviderRuntimeConfiguration:
    """Cấu hình runtime của một provider candidate."""

    provider: LlmProvider
    model_name: str
    api_keys: tuple[SecretStr, ...]
    base_url: str

    def for_key(self, key: SecretStr, options: tuple[float, int, float]) -> ChatModelConfiguration:
        """Tạo client configuration cho một credential."""
        temperature, max_tokens, timeout = options
        return ChatModelConfiguration(
            self.provider.value, self.model_name, key, self.base_url,
            temperature, max_tokens, timeout,
        )


@dataclass(frozen=True, slots=True)
class LlmRuntimeConfiguration:
    """Ordered provider candidates và policy cho một model profile."""

    candidates: tuple[ProviderRuntimeConfiguration, ...]
    temperature: float
    max_tokens: int
    timeout_seconds: float
    policy: LlmPolicyConfiguration

    @property
    def provider(self) -> str:
        """Compatibility metadata của primary provider."""
        return self.candidates[0].provider.value.casefold()

    @property
    def model_name(self) -> str:
        """Compatibility metadata của primary model."""
        return self.candidates[0].model_name

    @property
    def api_keys(self) -> tuple[SecretStr, ...]:
        """Compatibility key list của primary provider."""
        return self.candidates[0].api_keys

    @property
    def base_url(self) -> str:
        """Compatibility base URL của primary provider."""
        return self.candidates[0].base_url

    def for_key(self, key: SecretStr) -> ChatModelConfiguration:
        """Compatibility client config cho primary provider."""
        options = (self.temperature, self.max_tokens, self.timeout_seconds)
        return self.candidates[0].for_key(key, options)


def resolve_runtime_configuration(
    settings: Settings,
    overrides: tuple[str, float, int] | None = None,
    detector: CredentialProviderDetector | None = None,
) -> LlmRuntimeConfiguration:
    """Resolve ordered provider candidates theo precedence migration."""
    providers = _provider_priority(settings)
    resolver = detector or create_default_credential_detector()
    credentials = _credential_map(settings, providers, resolver)
    profile = "summary" if overrides else "default"
    candidates = tuple(
        _candidate(settings, provider, credentials[provider], profile, providers, overrides)
        for provider in providers
    )
    temperature, max_tokens = _model_options(settings, overrides)
    policy = LlmPolicyConfiguration(
        settings.llm_credential_cooldown_seconds,
        settings.llm_provider_failure_threshold,
        settings.llm_provider_cooldown_seconds,
    )
    return LlmRuntimeConfiguration(
        candidates, temperature, max_tokens,
        settings.llm_request_timeout_seconds, policy,
    )


def effective_api_keys(settings: Settings) -> tuple[SecretStr, ...]:
    """Giữ precedence key list/single-key của cấu hình legacy."""
    if settings.llm_api_keys is not None:
        return settings.llm_api_keys
    provider = LlmProvider.parse(settings.llm_provider)
    direct = settings.llm_api_key.strip()
    legacy = settings.google_api_key if provider is LlmProvider.GEMINI else settings.openai_api_key
    value = direct or legacy.strip()
    return (SecretStr(value),) if value else ()


def has_llm_configuration(settings: Settings) -> bool:
    """Kiểm tra cấu hình có ít nhất một ordered candidate hợp lệ."""
    try:
        return bool(resolve_runtime_configuration(settings).candidates)
    except (ValueError, IndexError):
        return False


def resolve_provider_config(api_key: str, base_url: str, model_name: str) -> tuple[str, str]:
    """Giữ tương thích OpenRouter/OpenAI-compatible explicit configuration."""
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
    """Nhận diện endpoint local cho migration guidance."""
    normalized = base_url.casefold()
    return "localhost" in normalized or "127.0.0.1" in normalized


def _provider_priority(settings: Settings) -> tuple[LlmProvider, ...]:
    raw = settings.llm_provider_priority or (settings.llm_provider,)
    providers = tuple(LlmProvider.parse(item) for item in raw if item.strip())
    if not providers or len(set(providers)) != len(providers):
        raise ValueError("LLM provider priority phải không rỗng và không trùng provider.")
    return providers


def _credential_map(
    settings: Settings,
    providers: tuple[LlmProvider, ...],
    detector: CredentialProviderDetector,
) -> dict[LlmProvider, tuple[SecretStr, ...]]:
    explicit = _explicit_credentials(settings)
    generic = settings.llm_api_keys or ()
    if not settings.llm_provider_priority:
        legacy = effective_api_keys(settings)
        if legacy:
            explicit[providers[0]] = legacy
        generic = ()
    detected = _detect_credentials(generic, detector)
    merged = {provider: explicit.get(provider, ()) + detected.get(provider, ()) for provider in providers}
    _validate_credentials(merged, providers)
    return merged


def _explicit_credentials(settings: Settings) -> dict[LlmProvider, tuple[SecretStr, ...]]:
    configured = {
        LlmProvider.GEMINI: settings.gemini_api_keys,
        LlmProvider.OPENAI: settings.openai_api_keys,
        LlmProvider.ANTHROPIC: settings.anthropic_api_keys,
    }
    if settings.google_api_key and not configured[LlmProvider.GEMINI]:
        configured[LlmProvider.GEMINI] = (SecretStr(settings.google_api_key.strip()),)
    if settings.openai_api_key and not configured[LlmProvider.OPENAI]:
        configured[LlmProvider.OPENAI] = (SecretStr(settings.openai_api_key.strip()),)
    return configured


def _detect_credentials(
    keys: tuple[SecretStr, ...], detector: CredentialProviderDetector
) -> dict[LlmProvider, tuple[SecretStr, ...]]:
    grouped: dict[LlmProvider, list[SecretStr]] = {}
    for key in keys:
        grouped.setdefault(detector.detect(key), []).append(key)
    return {provider: tuple(values) for provider, values in grouped.items()}


def _validate_credentials(
    credentials: dict[LlmProvider, tuple[SecretStr, ...]],
    providers: tuple[LlmProvider, ...],
) -> None:
    if any(not credentials[provider] for provider in providers):
        raise ValueError("Mỗi provider được ưu tiên phải có ít nhất một credential.")
    raw = [key.get_secret_value() for values in credentials.values() for key in values]
    if any(not value.strip() for value in raw) or len(set(raw)) != len(raw):
        raise ValueError("LLM credentials không được rỗng hoặc trùng giữa các provider.")


def _candidate(
    settings: Settings,
    provider: LlmProvider,
    keys: tuple[SecretStr, ...],
    profile: ModelProfile,
    providers: tuple[LlmProvider, ...],
    overrides: tuple[str, float, int] | None,
) -> ProviderRuntimeConfiguration:
    model = _model_name(settings, provider, profile, providers, overrides)
    if not model:
        raise ValueError("Mỗi provider được ưu tiên phải có model hợp lệ.")
    base_url = _base_url(settings, provider)
    if provider is LlmProvider.OPENAI:
        base_url, model = resolve_provider_config(keys[0].get_secret_value(), base_url, model)
    return ProviderRuntimeConfiguration(provider, model, keys, base_url)


def _model_name(
    settings: Settings,
    provider: LlmProvider,
    profile: ModelProfile,
    providers: tuple[LlmProvider, ...],
    overrides: tuple[str, float, int] | None,
) -> str:
    base = _provider_models(settings)[provider].strip()
    if not base and len(providers) == 1:
        base = settings.model_name.strip()
    summary = _summary_models(settings)[provider].strip()
    legacy_summary = overrides[0].strip() if overrides else ""
    if profile == "summary" and legacy_summary and len(providers) > 1 and not summary:
        raise ValueError("Summary model legacy không dùng được với multi-provider priority.")
    return summary or legacy_summary or base


def _provider_models(settings: Settings) -> dict[LlmProvider, str]:
    return {
        LlmProvider.GEMINI: settings.gemini_model,
        LlmProvider.OPENAI: settings.openai_model,
        LlmProvider.ANTHROPIC: settings.anthropic_model,
    }


def _summary_models(settings: Settings) -> dict[LlmProvider, str]:
    return {
        LlmProvider.GEMINI: settings.gemini_summary_model,
        LlmProvider.OPENAI: settings.openai_summary_model,
        LlmProvider.ANTHROPIC: settings.anthropic_summary_model,
    }


def _base_url(settings: Settings, provider: LlmProvider) -> str:
    if provider is LlmProvider.OPENAI:
        return (settings.llm_base_url or settings.openai_base_url).strip()
    if provider is LlmProvider.ANTHROPIC:
        return settings.anthropic_base_url.strip()
    return ""


def _model_options(settings: Settings, overrides: tuple[str, float, int] | None) -> tuple[float, int]:
    if overrides:
        return overrides[1], overrides[2]
    return settings.llm_temperature, settings.agent_max_output_tokens
