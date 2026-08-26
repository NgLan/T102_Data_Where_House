"""Dịch lỗi LLM sang InfrastructureException với message đã kiểm soát."""

from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.llm.failure_classifier import LlmFailureDecision

ERROR_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.LLM_ERROR: "Lỗi khi gọi mô hình ngôn ngữ.",
    ErrorCode.LLM_MODEL_NOT_FOUND: "Mô hình LLM không tồn tại hoặc không được provider hỗ trợ.",
    ErrorCode.LLM_AUTHENTICATION_ERROR: "Xác thực với LLM provider thất bại.",
    ErrorCode.LLM_RATE_LIMIT_ERROR: "LLM provider đang giới hạn tần suất yêu cầu.",
    ErrorCode.LLM_QUOTA_EXCEEDED: "Hạn ngạch LLM provider đã cạn.",
    ErrorCode.LLM_TIMEOUT_ERROR: "Kết nối tới LLM provider bị quá thời gian chờ.",
    ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR: "Structured output của LLM không hợp lệ.",
}


def translate_llm_failure(decision: LlmFailureDecision) -> InfrastructureException:
    """Tạo exception ổn định mà không sao chép raw provider message."""
    return InfrastructureException(decision.code, ERROR_MESSAGES[decision.code])
