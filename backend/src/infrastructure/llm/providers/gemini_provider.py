"""Google Gemini provider adapter."""

from langchain_core.language_models import BaseChatModel
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.llm.provider_registry_types import ChatModelConfiguration


class GeminiLlmProvider:
    """Dựng Gemini client qua LangChain integration chính thức."""

    @property
    def name(self) -> str:
        """Trả canonical provider name."""
        return "GEMINI"

    def build(self, configuration: ChatModelConfiguration) -> BaseChatModel:
        """Dựng Gemini client hoặc dịch lỗi thiếu dependency."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=configuration.model_name,
                google_api_key=configuration.api_key.get_secret_value(),
                temperature=configuration.temperature,
                max_output_tokens=configuration.max_tokens,
                timeout=configuration.timeout_seconds,
                max_retries=0,
            )
        except Exception as exc:
            raise InfrastructureException(
                ErrorCode.LLM_ERROR,
                "Không thể khởi tạo Gemini LLM provider.",
            ) from exc
