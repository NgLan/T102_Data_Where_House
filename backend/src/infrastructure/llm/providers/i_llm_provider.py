"""Contract chung cho provider adapter."""

from typing import Protocol

from langchain_core.language_models import BaseChatModel
from src.infrastructure.llm.provider_registry_types import ChatModelConfiguration


class ILLMProvider(Protocol):
    """Dựng một provider client từ cấu hình trung lập."""

    @property
    def name(self) -> str:
        """Trả canonical provider name."""
        ...

    def build(self, configuration: ChatModelConfiguration) -> BaseChatModel:
        """Dựng client đã tắt automatic SDK retry."""
        ...
