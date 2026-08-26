"""Validation application cho một câu trả lời clarification."""

from src.application.project_sessions.input import AnswerClarificationInput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.clarification import ClarificationQuestionMetadata
from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.enums import ClarificationAnswerKind


def resolve_clarification_answer(
    question: SessionEvent, data: AnswerClarificationInput
) -> tuple[str, ClarificationAnswerKind, int | None]:
    """Chuẩn hóa option hoặc custom answer mà không phụ thuộc HTTP."""
    metadata = question.metadata
    if not isinstance(metadata, ClarificationQuestionMetadata):
        raise_stale_clarification()
    if data.option_index is not None:
        return _resolve_option(metadata, data.option_index)
    custom = (data.custom_answer or "").strip()
    if not custom:
        raise BusinessException(
            ErrorCode.VALIDATION_ERROR,
            "Câu trả lời tùy chỉnh là bắt buộc.",
        )
    return custom, ClarificationAnswerKind.CUSTOM, None


def raise_stale_clarification() -> None:
    """Phát conflict thống nhất cho answer trùng hoặc sai question."""
    raise BusinessException(
        ErrorCode.SESSION_CLARIFICATION_STALE,
        "Clarification không còn chờ câu trả lời.",
    )


def _resolve_option(
    metadata: ClarificationQuestionMetadata, option_index: int
) -> tuple[str, ClarificationAnswerKind, int]:
    if option_index < 0 or option_index >= len(metadata.options):
        raise BusinessException(ErrorCode.VALIDATION_ERROR, "Lựa chọn không hợp lệ.")
    return metadata.options[option_index], ClarificationAnswerKind.OPTION, option_index
