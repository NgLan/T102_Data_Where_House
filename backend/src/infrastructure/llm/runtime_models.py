"""Resolve provider-specific model candidates cho một logical profile."""

from dataclasses import dataclass

from config import Settings
from pydantic import SecretStr
from src.infrastructure.llm.openai_compatibility import resolve_provider_config
from src.infrastructure.llm.provider_types import LlmProvider


@dataclass(frozen=True, slots=True)
class ModelCandidate:
    """Provider/model/key/base-url candidate trước khi dựng client."""

    provider: LlmProvider
    model_name: str
    api_keys: tuple[SecretStr, ...]
    base_url: str


@dataclass(frozen=True, slots=True)
class ModelResolutionInput:
    """Gom input để giữ function signature trong giới hạn."""

    settings: Settings
    providers: tuple[LlmProvider, ...]
    credentials: dict[LlmProvider, tuple[SecretStr, ...]]
    overrides: tuple[str, float, int] | None


def resolve_model_candidates(value: ModelResolutionInput) -> tuple[ModelCandidate, ...]:
    """Resolve đúng một model cho mỗi ordered provider."""
    return tuple(_candidate(provider, value) for provider in value.providers)


def model_options(settings: Settings, overrides: tuple[str, float, int] | None) -> tuple[float, int]:
    """Resolve temperature/max-token của logical profile."""
    if overrides:
        return overrides[1], overrides[2]
    return settings.llm_temperature, settings.agent_max_output_tokens


def _candidate(provider: LlmProvider, value: ModelResolutionInput) -> ModelCandidate:
    model = _model_name(provider, value)
    if not model:
        raise ValueError("Mỗi provider được ưu tiên phải có model hợp lệ.")
    base_url = _base_url(value.settings, provider)
    keys = value.credentials[provider]
    if provider is LlmProvider.OPENAI:
        base_url, model = resolve_provider_config(keys[0].get_secret_value(), base_url, model)
    return ModelCandidate(provider, model, keys, base_url)


def _model_name(provider: LlmProvider, value: ModelResolutionInput) -> str:
    settings = value.settings
    base = _provider_models(settings)[provider].strip()
    if not base and len(value.providers) == 1:
        base = settings.model_name.strip()
    summary = _summary_models(settings)[provider].strip()
    legacy_summary = value.overrides[0].strip() if value.overrides else ""
    if legacy_summary and len(value.providers) > 1 and not summary:
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
