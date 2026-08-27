"""Xác định provider của generic credential bằng pattern tập trung."""

from dataclasses import dataclass

from pydantic import SecretStr
from src.infrastructure.llm.provider_types import LlmProvider


@dataclass(frozen=True, slots=True)
class ProviderKeyPattern:
    """Một nhóm prefix thuộc đúng một provider."""

    provider: LlmProvider
    prefixes: tuple[str, ...]


class CredentialProviderDetector:
    """Detector không đoán provider khi không có kết quả duy nhất."""

    def __init__(self, patterns: tuple[ProviderKeyPattern, ...]) -> None:
        self._patterns = patterns

    def detect(self, credential: SecretStr) -> LlmProvider:
        """Trả provider duy nhất hoặc báo lỗi cấu hình an toàn."""
        raw = credential.get_secret_value()
        matches = {
            pattern.provider
            for pattern in self._patterns
            if any(raw.startswith(prefix) for prefix in pattern.prefixes)
        }
        if len(matches) != 1:
            raise ValueError("Generic LLM credential không xác định được provider duy nhất.")
        return matches.pop()


def create_default_credential_detector() -> CredentialProviderDetector:
    """Tạo detector với pattern cụ thể đứng trước pattern tổng quát."""
    patterns = (
        ProviderKeyPattern(LlmProvider.ANTHROPIC, ("sk-ant-",)),
        ProviderKeyPattern(LlmProvider.OPENAI, ("sk-or-v1-",)),
        ProviderKeyPattern(LlmProvider.GEMINI, ("AIza",)),
        ProviderKeyPattern(LlmProvider.OPENAI, ("sk-",)),
    )
    return CredentialProviderDetector(patterns)

