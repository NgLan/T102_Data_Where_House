"""Typed multi-provider LLM runtime configuration facade."""

from dataclasses import dataclass

from config import Settings
from pydantic import SecretStr
from src.infrastructure.llm.credential_detector import (
    CredentialProviderDetector,
    create_default_credential_detector,
)
from src.infrastructure.llm.openai_compatibility import (
    OPENROUTER_BASE_URL,
    is_local_endpoint,
    resolve_provider_config,
)
from src.infrastructure.llm.provider_registry_types import ChatModelConfiguration
from src.infrastructure.llm.provider_types import LlmPolicyConfiguration, LlmProvider
from src.infrastructure.llm.runtime_credentials import (
    effective_api_keys,
    resolve_credentials,
    resolve_provider_priority,
)
from src.infrastructure.llm.runtime_models import (
    ModelResolutionInput,
    model_options,
    resolve_model_candidates,
)


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
    """Resolve ordered provider/model/credential candidates."""
    providers = resolve_provider_priority(settings)
    resolver = detector or create_default_credential_detector()
    credentials = resolve_credentials(settings, providers, resolver)
    model_input = ModelResolutionInput(settings, providers, credentials, overrides)
    raw_candidates = resolve_model_candidates(model_input)
    candidates = tuple(
        ProviderRuntimeConfiguration(item.provider, item.model_name, item.api_keys, item.base_url)
        for item in raw_candidates
    )
    temperature, max_tokens = model_options(settings, overrides)
    policy = LlmPolicyConfiguration(
        settings.llm_credential_cooldown_seconds,
        settings.llm_provider_failure_threshold,
        settings.llm_provider_cooldown_seconds,
    )
    return LlmRuntimeConfiguration(
        candidates, temperature, max_tokens,
        settings.llm_request_timeout_seconds, policy,
    )


def has_llm_configuration(settings: Settings) -> bool:
    """Kiểm tra cấu hình có ít nhất một ordered candidate hợp lệ."""
    try:
        return bool(resolve_runtime_configuration(settings).candidates)
    except (ValueError, IndexError):
        return False


__all__ = [
    "OPENROUTER_BASE_URL",
    "LlmRuntimeConfiguration",
    "ProviderRuntimeConfiguration",
    "effective_api_keys",
    "has_llm_configuration",
    "is_local_endpoint",
    "resolve_provider_config",
    "resolve_runtime_configuration",
]
