"""Factory duy nhất tạo event quan sát được của phiên Agent."""

from src.application.project_sessions.session_event_inputs import (
    AgentCallEventInput,
    AgentMessageEventInput,
    AgentResultEventInput,
    AnswerEventInput,
    QuestionEventInput,
    UserEventInput,
)
from src.domain.project_session.clarification import (
    ClarificationAnswerMetadata,
    ClarificationQuestionMetadata,
)
from src.domain.project_session.entities import SessionEvent
from src.domain.project_session.enums import (
    AgentType,
    SessionEventRole,
    SessionEventType,
)
from src.domain.project_session.value_objects import (
    AgentCallMetadata,
    AgentResultMetadata,
    MessageMetadata,
)
from src.domain.shared.types import EntityID


def create_user_event(data: UserEventInput) -> SessionEvent:
    """Tạo message khởi đầu một lượt mới từ người dùng."""
    return SessionEvent(
        session_id=data.session_id,
        turn_id=data.turn_id,
        role=SessionEventRole.USER,
        type=SessionEventType.MESSAGE,
        content=data.content,
    )


def create_agent_call(
    session_id: EntityID,
    turn_id: EntityID,
) -> SessionEvent:
    """Tạo mốc bắt đầu Agent không lưu raw prompt."""
    return create_typed_agent_call(
        AgentCallEventInput(
            session_id,
            turn_id,
            AgentType.DW_DESIGN,
            "session-conversation",
        )
    )


def create_typed_agent_call(data: AgentCallEventInput) -> SessionEvent:
    """Tạo Agent call cho workflow có agent và operation riêng."""
    return SessionEvent(
        session_id=data.session_id,
        turn_id=data.turn_id,
        role=SessionEventRole.AGENT,
        type=SessionEventType.AGENT_CALL,
        metadata=AgentCallMetadata(
            AgentType.ORCHESTRATOR,
            data.target_agent,
            data.operation,
        ),
    )


def create_question(data: QuestionEventInput) -> SessionEvent:
    """Tạo câu hỏi làm rõ hiển thị cho người dùng."""
    return SessionEvent(
        session_id=data.session_id,
        turn_id=data.turn_id,
        role=SessionEventRole.AGENT,
        type=SessionEventType.QUESTION,
        content=data.question,
        metadata=ClarificationQuestionMetadata(
            data.options,
            data.allow_custom_answer,
            data.reason,
            data.original_intent,
            data.missing_information,
        ),
    )


def create_answer(data: AnswerEventInput) -> SessionEvent:
    """Tạo answer tham chiếu chính xác question được trả lời."""
    return SessionEvent(
        session_id=data.session_id,
        turn_id=data.turn_id,
        role=SessionEventRole.USER,
        type=SessionEventType.ANSWER,
        content=data.content,
        metadata=ClarificationAnswerMetadata(data.question_id, data.kind, data.option_index),
    )


def create_agent_result(data: AgentResultEventInput) -> SessionEvent:
    """Tạo kết quả Agent với metadata công khai tối thiểu."""
    call_metadata = data.call.metadata
    agent = (
        call_metadata.target_agent
        if isinstance(call_metadata, AgentCallMetadata)
        else AgentType.DW_DESIGN
    )
    return SessionEvent(
        session_id=data.call.session_id,
        turn_id=data.call.turn_id,
        role=SessionEventRole.AGENT,
        type=SessionEventType.AGENT_RESULT,
        content=data.content,
        metadata=AgentResultMetadata(
            agent,
            data.status,
            data.call.id,
            output_data=data.output,
        ),
    )


def create_agent_message(data: AgentMessageEventInput) -> SessionEvent:
    """Tạo public Agent message liên kết technical result tương ứng."""
    return SessionEvent(
        session_id=data.result.session_id,
        turn_id=data.result.turn_id,
        role=SessionEventRole.AGENT,
        type=SessionEventType.MESSAGE,
        content=data.content,
        metadata=MessageMetadata(
            agent_result_id=data.result.id,
            proposal_change_id=data.proposal_change_id,
        ),
    )
