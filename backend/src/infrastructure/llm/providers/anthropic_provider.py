"""Anthropic provider adapter."""

from langchain_core.language_models import BaseChatModel
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.llm.provider_registry_types import ChatModelConfiguration


class AnthropicLlmProvider:
    """Dựng Anthropic client khi integration đã được cài đặt."""

    @property
    def name(self) -> str:
        """Trả canonical provider name."""
        return "ANTHROPIC"

    def build(self, configuration: ChatModelConfiguration) -> BaseChatModel:
        """Dựng Anthropic client hoặc dịch lỗi thiếu dependency."""
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
        try:
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(**options)
        except Exception as exc:
            raise InfrastructureException(
                ErrorCode.LLM_ERROR,
                "Không thể khởi tạo Anthropic LLM provider.",
            ) from exc
