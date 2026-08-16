"""Khởi tạo mô hình ngôn ngữ (Chat Model) dùng chung cho toàn bộ AI Agent."""

from config import Settings, get_settings
from langchain_openai import ChatOpenAI
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger

logger = get_logger(__name__)


def build_chat_model(settings: Settings | None = None) -> ChatOpenAI:
    """Tạo Chat Model từ cấu hình hệ thống.

    Toàn bộ tham số lấy từ biến môi trường (`MODEL_NAME`, `LLM_TEMPERATURE`, `MAX_TOKENS`,
    `OPENAI_API_KEY`) — tuyệt đối không hard-code giá trị nào trong mã nguồn.
    """
    app_settings = settings or get_settings()

    if not app_settings.openai_api_key:
        raise InfrastructureException(
            code=ErrorCode.LLM_ERROR,
            message="Chưa cấu hình OPENAI_API_KEY nên không thể khởi tạo mô hình ngôn ngữ.",
        )

    try:
        return ChatOpenAI(
            model=app_settings.model_name,
            temperature=app_settings.llm_temperature,
            max_tokens=app_settings.max_tokens,
            api_key=app_settings.openai_api_key,
            timeout=app_settings.llm_request_timeout_seconds,
        )
    except Exception as exc:
        logger.exception("Khởi tạo Chat Model thất bại.")
        raise InfrastructureException(
            code=ErrorCode.LLM_ERROR,
            message="Không thể khởi tạo mô hình ngôn ngữ.",
        ) from exc
