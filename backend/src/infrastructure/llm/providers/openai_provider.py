"""OpenAI/OpenRouter/OpenAI-compatible provider adapter."""

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from src.infrastructure.llm.provider_registry_types import ChatModelConfiguration


class OpenAILlmProvider:
    """Dựng OpenAI-compatible client với retry do gateway quản lý."""

    @property
    def name(self) -> str:
        """Trả canonical provider name."""
        return "OPENAI"

    def build(self, configuration: ChatModelConfiguration) -> BaseChatModel:
        """Dựng OpenAI client mà không gọi network."""
        options: dict[str, object] = {
            "model": configuration.model_name,
            "api_key": configuration.api_key.get_secret_value(),
            "temperature": configuration.temperature,
            "max_tokens": configuration.max_tokens,
            "timeout": configuration.timeout_seconds,
            "max_retries": 0,
        }
        if configuration.base_url:
            options["base_url"] = configuration.base_url
        return ChatOpenAI(**options)

