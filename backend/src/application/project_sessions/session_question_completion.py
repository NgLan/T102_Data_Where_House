"""Tạo event và output khi Agent cần clarification tiếp theo."""

from src.application.data_warehouse_workflows.output import AgentTurnOutput
from src.application.project_sessions.output import SessionTurnOutput
from src.application.project_sessions.session_event_factory import (
    QuestionEventInput,
    create_question,
)
from src.domain.project_session.entities import ProjectSession, SessionEvent


def create_question_event(
    session: ProjectSession,
    call: SessionEvent,
    result: AgentTurnOutput,
) -> SessionEvent:
    """Tạo structured QUESTION bằng đúng turn đang chạy."""
    if call.turn_id is None:
        raise ValueError("Agent call must have a turn ID.")
    return create_question(
        QuestionEventInput(
            session.id,
            call.turn_id,
            result.question or "Please provide more information.",
            result.options,
            result.allow_custom_answer,
            result.reason,
            result.original_intent,
            result.reason,
        )
    )


def create_question_turn_output(
    session: ProjectSession,
    event: SessionEvent,
    result: AgentTurnOutput,
) -> SessionTurnOutput:
    """Xuất question vừa persist mà không lộ metadata nội bộ."""
    if event.turn_id is None:
        raise ValueError("Clarification question must have a turn ID.")
    return SessionTurnOutput(
        session.id,
        event.turn_id,
        result.kind,
        question_id=event.id,
        question=event.content,
        options=result.options,
        allow_custom_answer=result.allow_custom_answer,
        reason=result.reason,
        summary=result.summary,
    )
