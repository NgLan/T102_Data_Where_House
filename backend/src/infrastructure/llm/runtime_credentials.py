"""Resolve provider priority và credential precedence."""

from config import Settings
from pydantic import SecretStr
from src.infrastructure.llm.credential_detector import CredentialProviderDetector
from src.infrastructure.llm.provider_types import LlmProvider


def resolve_provider_priority(settings: Settings) -> tuple[LlmProvider, ...]:
    """Normalize ordered priority mới hoặc legacy singleton provider."""
    raw = settings.llm_provider_priority or (settings.llm_provider,)
    providers = tuple(LlmProvider.parse(item) for item in raw if item.strip())
    if not providers or len(set(providers)) != len(providers):
        raise ValueError("LLM provider priority phải không rỗng và không trùng provider.")
    return providers


def resolve_credentials(
    settings: Settings,
    providers: tuple[LlmProvider, ...],
    detector: CredentialProviderDetector,
) -> dict[LlmProvider, tuple[SecretStr, ...]]:
    """Merge explicit, generic-detected và legacy fallback credentials."""
    explicit = _explicit_credentials(settings)
    generic = settings.llm_api_keys or ()
    if not settings.llm_provider_priority:
        legacy = effective_api_keys(settings)
        if legacy:
            explicit[providers[0]] = legacy
        generic = ()
    detected = _detect_credentials(generic, detector)
    if set(detected).difference(providers):
        raise ValueError("Generic credential thuộc provider không có trong priority.")
    merged = {provider: explicit.get(provider, ()) + detected.get(provider, ()) for provider in providers}
    _add_legacy_fallbacks(settings, providers, merged)
    _validate_credentials(merged, providers)
    return merged


def effective_api_keys(settings: Settings) -> tuple[SecretStr, ...]:
    """Giữ precedence key list/single-key của cấu hình legacy."""
    if settings.llm_api_keys is not None:
        return settings.llm_api_keys
    provider = LlmProvider.parse(settings.llm_provider)
    direct = settings.llm_api_key.strip()
    legacy = settings.google_api_key if provider is LlmProvider.GEMINI else settings.openai_api_key
    value = direct or legacy.strip()
    return (SecretStr(value),) if value else ()


def _explicit_credentials(settings: Settings) -> dict[LlmProvider, tuple[SecretStr, ...]]:
    return {
        LlmProvider.GEMINI: settings.gemini_api_keys,
        LlmProvider.OPENAI: settings.openai_api_keys,
        LlmProvider.ANTHROPIC: settings.anthropic_api_keys,
    }


def _add_legacy_fallbacks(
    settings: Settings,
    providers: tuple[LlmProvider, ...],
    merged: dict[LlmProvider, tuple[SecretStr, ...]],
) -> None:
    legacy = {
        LlmProvider.GEMINI: settings.google_api_key.strip(),
        LlmProvider.OPENAI: settings.openai_api_key.strip(),
        LlmProvider.ANTHROPIC: "",
    }
    for provider in providers:
        if not merged[provider] and legacy[provider]:
            merged[provider] = (SecretStr(legacy[provider]),)


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
