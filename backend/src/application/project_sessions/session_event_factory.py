"""Factory duy nhất tạo event quan sát được của phiên Agent."""

from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.enums import AgentResultStatus, AgentType, SessionEventRole, SessionEventType
from src.domain.project_session.value_objects import AgentCallMetadata, AgentResultMetadata
from src.domain.shared.types import EntityID


def create_user_event(
    session_id: EntityID,
    turn_id: EntityID,
    content: str,
    is_answer: bool,
) -> SessionEvent:
    """Tạo message hoặc answer từ người dùng."""
    event_type = SessionEventType.ANSWER if is_answer else SessionEventType.MESSAGE
    return SessionEvent(
        session_id=session_id,
        turn_id=turn_id,
        role=SessionEventRole.USER,
        type=event_type,
        content=content,
    )


def create_agent_call(session_id: EntityID, turn_id: EntityID) -> SessionEvent:
    """Tạo mốc bắt đầu Agent không lưu raw prompt."""
    return SessionEvent(
        session_id=session_id,
        turn_id=turn_id,
        role=SessionEventRole.AGENT,
        type=SessionEventType.AGENT_CALL,
        metadata=AgentCallMetadata(
            AgentType.ORCHESTRATOR,
            AgentType.DW_DESIGN,
            "session-conversation",
        ),
    )


def create_question(session_id: EntityID, turn_id: EntityID, question: str) -> SessionEvent:
    """Tạo câu hỏi làm rõ hiển thị cho người dùng."""
    return SessionEvent(
        session_id=session_id,
        turn_id=turn_id,
        role=SessionEventRole.AGENT,
        type=SessionEventType.QUESTION,
        content=question,
    )


def create_agent_result(
    call: SessionEvent,
    status: AgentResultStatus,
    content: str,
    output: str | None = None,
) -> SessionEvent:
    """Tạo kết quả Agent với metadata công khai tối thiểu."""
    return SessionEvent(
        session_id=call.session_id,
        turn_id=call.turn_id,
        role=SessionEventRole.AGENT,
        type=SessionEventType.AGENT_RESULT,
        content=content,
        metadata=AgentResultMetadata(
            AgentType.DW_DESIGN,
            status,
            call.id,
            output_data=output,
        ),
    )
