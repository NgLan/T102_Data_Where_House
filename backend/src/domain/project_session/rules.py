"""Quy tắc nghiệp vụ cho sự kiện trong phiên Agent."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.enums import SessionEventRole, SessionEventType
from src.domain.project_session.value_objects import (
    AgentCallMetadata,
    AgentResultMetadata,
    MessageMetadata,
    SessionEventMetadata,
    ToolCallMetadata,
    ToolResultMetadata,
)
from src.domain.shared.types import EntityID

_CONTENT_EVENT_TYPES = frozenset(
    {SessionEventType.MESSAGE, SessionEventType.QUESTION, SessionEventType.ANSWER}
)
_ALLOWED_ROLES: dict[SessionEventType, frozenset[SessionEventRole]] = {
    SessionEventType.MESSAGE: frozenset({SessionEventRole.USER, SessionEventRole.AGENT}),
    SessionEventType.QUESTION: frozenset({SessionEventRole.AGENT}),
    SessionEventType.ANSWER: frozenset({SessionEventRole.USER}),
    SessionEventType.AGENT_CALL: frozenset({SessionEventRole.AGENT}),
    SessionEventType.AGENT_RESULT: frozenset({SessionEventRole.AGENT}),
    SessionEventType.TOOL_CALL: frozenset({SessionEventRole.AGENT}),
    SessionEventType.TOOL_RESULT: frozenset({SessionEventRole.TOOL}),
}
_METADATA_TYPES: dict[SessionEventType, type[SessionEventMetadata]] = {
    SessionEventType.MESSAGE: MessageMetadata,
    SessionEventType.AGENT_CALL: AgentCallMetadata,
    SessionEventType.AGENT_RESULT: AgentResultMetadata,
    SessionEventType.TOOL_CALL: ToolCallMetadata,
    SessionEventType.TOOL_RESULT: ToolResultMetadata,
}


def validate_session_event_ref(session_id: EntityID) -> None:
    """Kiểm tra tham chiếu tới phiên làm việc.

    Args:
        session_id: Định danh phiên mà event tham chiếu.

    Raises:
        BusinessException: Khi session ID không hợp lệ.
    """
    if not session_id:
        raise BusinessException(
            code=ErrorCode.INVALID_SESSION_EVENT_REF,
            message="Sự kiện phiên làm việc phải thuộc về một session_id hợp lệ.",
        )


def validate_session_event_shape(
    role: SessionEventRole,
    event_type: SessionEventType,
    content: str | None,
) -> None:
    """Kiểm tra cặp role/event và yêu cầu nội dung.

    Args:
        role: Vai trò phát event.
        event_type: Loại event.
        content: Nội dung hội thoại tùy chọn.

    Raises:
        BusinessException: Khi role/event sai matrix hoặc thiếu nội dung bắt buộc.
    """
    if role not in _ALLOWED_ROLES[event_type]:
        _raise_validation("Vai trò không phù hợp với loại sự kiện phiên.")
    if event_type in _CONTENT_EVENT_TYPES and not (content or "").strip():
        _raise_validation("Sự kiện hội thoại phải có nội dung.")


def validate_session_metadata(
    event_type: SessionEventType,
    metadata: SessionEventMetadata | None,
) -> None:
    """Kiểm tra metadata tương ứng với từng loại sự kiện.

    Args:
        event_type: Loại event quyết định schema metadata.
        metadata: Metadata cần kiểm tra.

    Raises:
        BusinessException: Khi metadata thiếu, thừa hoặc sai loại.
    """
    expected = _METADATA_TYPES.get(event_type)
    if expected is None and metadata is not None:
        _raise_validation("Loại sự kiện này không chấp nhận metadata.")
    if expected is not None and metadata is not None and not isinstance(metadata, expected):
        _raise_validation("Metadata không phù hợp với loại sự kiện phiên.")
    if event_type not in {SessionEventType.MESSAGE, SessionEventType.QUESTION, SessionEventType.ANSWER}:
        if metadata is None:
            _raise_validation("Sự kiện Agent hoặc Tool phải có metadata.")


def _raise_validation(message: str) -> None:
    """Ném lỗi validation thống nhất cho hình dạng sự kiện."""
    raise BusinessException(code=ErrorCode.VALIDATION_ERROR, message=message)
