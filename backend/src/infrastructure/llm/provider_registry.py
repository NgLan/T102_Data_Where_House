"""Registry extensible cho các LLM provider adapter."""

from collections.abc import Callable

from langchain_core.language_models import BaseChatModel
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.llm.provider_registry_types import ChatModelConfiguration
from src.infrastructure.llm.provider_types import LlmProvider
from src.infrastructure.llm.providers import (
    AnthropicLlmProvider,
    GeminiLlmProvider,
    OpenAILlmProvider,
)
from src.infrastructure.llm.providers.i_llm_provider import ILLMProvider

ProviderBuilder = Callable[[ChatModelConfiguration], BaseChatModel]


class ChatModelProviderRegistry:
    """Ánh xạ provider name sang adapter mà không sửa Agent."""

    def __init__(self) -> None:
        self._builders: dict[str, ProviderBuilder] = {}

    @property
    def supported_providers(self) -> frozenset[str]:
        """Trả canonical provider names đã đăng ký."""
        return frozenset(self._builders)

    def register(self, provider: str, builder: ProviderBuilder) -> None:
        """Đăng ký builder tương thích extension/test hiện tại."""
        self._builders[_normalize(provider)] = builder

    def register_adapter(self, adapter: ILLMProvider) -> None:
        """Đăng ký provider adapter theo contract chung."""
        self.register(adapter.name, adapter.build)

    def build(self, configuration: ChatModelConfiguration) -> BaseChatModel:
        """Dựng model hoặc báo lỗi cấu hình provider an toàn."""
        builder = self._builders.get(_normalize(configuration.provider))
        if builder is None:
            raise InfrastructureException(
                ErrorCode.LLM_ERROR,
                "LLM provider chưa được đăng ký.",
            )
        return builder(configuration)


def create_default_provider_registry() -> ChatModelProviderRegistry:
    """Tạo registry OpenAI, Gemini và Anthropic."""
    registry = ChatModelProviderRegistry()
    registry.register_adapter(OpenAILlmProvider())
    registry.register_adapter(GeminiLlmProvider())
    registry.register_adapter(AnthropicLlmProvider())
    return registry


def _normalize(provider: str) -> str:
    try:
        return LlmProvider.parse(provider).value.casefold()
    except ValueError:
        return provider.strip().casefold()


__all__ = [
    "ChatModelConfiguration",
    "ChatModelProviderRegistry",
    "create_default_provider_registry",
]

