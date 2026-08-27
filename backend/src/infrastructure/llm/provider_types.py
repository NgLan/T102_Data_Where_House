"""Các kiểu provider/model trung lập dùng trong LLM Infrastructure."""

from dataclasses import dataclass
from enum import StrEnum

from pydantic import SecretStr


class LlmProvider(StrEnum):
    """Provider canonical sau khi normalize cấu hình legacy."""

    OPENAI = "OPENAI"
    GEMINI = "GEMINI"
    ANTHROPIC = "ANTHROPIC"

    @classmethod
    def parse(cls, value: str) -> "LlmProvider":
        """Normalize tên provider và alias đang được hỗ trợ."""
        normalized = value.strip().casefold()
        aliases = {"google": cls.GEMINI, "openai_compatible": cls.OPENAI}
        if normalized in aliases:
            return aliases[normalized]
        try:
            return cls(normalized.upper())
        except ValueError as exc:
            raise ValueError("LLM provider chưa được hỗ trợ.") from exc


@dataclass(frozen=True, slots=True)
class ProviderModelConfiguration:
    """Cấu hình model cho một provider candidate."""

    provider: LlmProvider
    model_name: str
    base_url: str


@dataclass(frozen=True, slots=True)
class ProviderCredentialConfiguration:
    """Credential đã được gán provider, chỉ tồn tại trong Infrastructure."""

    provider: LlmProvider
    keys: tuple[SecretStr, ...]


@dataclass(frozen=True, slots=True)
class LlmPolicyConfiguration:
    """Operational policy cho credential/provider cooldown."""

    credential_cooldown_seconds: float
    provider_failure_threshold: int
    provider_cooldown_seconds: float

