"""Question persistence for Agent tool mode selection and confirmation."""

from dataclasses import dataclass

from src.application.agent_tools import AgentToolPreparation
from src.application.data_warehouse_workflows.output import AgentTurnKind
from src.application.project_sessions.output import SessionTurnOutput
from src.application.project_sessions.session_event_factory import QuestionEventInput, create_question
from src.application.project_sessions.session_tool_event_writer import SessionToolEventWriter
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import SessionQuestionKind


@dataclass(frozen=True, slots=True)
class ToolQuestionDependencies:
    writer: SessionToolEventWriter


@dataclass(frozen=True, slots=True)
class ToolQuestionDraft:
    content: str
    options: tuple[str, ...]
    kind: SessionQuestionKind


@dataclass(frozen=True, slots=True)
class ToolQuestionContext:
    session: ProjectSession
    call: SessionEvent
    prepared: AgentToolPreparation
    draft: ToolQuestionDraft


class SessionToolQuestionWriter:
    def __init__(self, dependencies: ToolQuestionDependencies) -> None:
        self._dependencies = dependencies

    async def ask_mode(
        self, session: ProjectSession, call: SessionEvent, prepared: AgentToolPreparation
    ) -> SessionTurnOutput:
        draft = ToolQuestionDraft(
            "Chọn cách triển khai DDL vào Sandbox.",
            ("Giữ nguyên schema", "Reset schema", "Hủy"),
            SessionQuestionKind.SANDBOX_MODE_SELECTION,
        )
        return await self._persist(ToolQuestionContext(session, call, prepared, draft))

    async def ask_confirmation(
        self, session: ProjectSession, call: SessionEvent, prepared: AgentToolPreparation
    ) -> SessionTurnOutput:
        request = prepared.request
        action = (
            f"reset toàn bộ schema `{prepared.schema_name}`"
            if request.reset_schema
            else "giữ nguyên schema và thực thi DDL"
        )
        content = (
            f"Xác nhận chạy target {request.target.kind.value} revision {prepared.revision} "
            f"(current {prepared.current_revision}, base {prepared.base_revision}) "
            f"trên schema `{prepared.schema_name}`; endpoint risk {prepared.endpoint_risk}; "
            f"thao tác sẽ {action}."
        )
        draft = ToolQuestionDraft(content, ("Xác nhận", "Hủy"), SessionQuestionKind.TOOL_CONFIRMATION)
        return await self._persist(ToolQuestionContext(session, call, prepared, draft))

    async def _persist(self, data: ToolQuestionContext) -> SessionTurnOutput:
        session, call = data.session, data.call
        prepared, draft = data.prepared, data.draft
        if call.turn_id is None:
            raise ValueError("Agent call must have a turn ID.")
        event = create_question(_question_input(data))
        session.wait_for_clarification(call.turn_id, event.id)
        await self._dependencies.writer.persist(session, (event,))
        return SessionTurnOutput(
            session.id,
            call.turn_id,
            AgentTurnKind.CONFIRMATION_REQUIRED,
            question_id=event.id,
            question=draft.content,
            options=draft.options,
            question_kind=draft.kind,
            tool_name=prepared.request.name,
        )


def _question_input(data: ToolQuestionContext) -> QuestionEventInput:
    session, call = data.session, data.call
    prepared, draft = data.prepared, data.draft
    request = prepared.request
    return QuestionEventInput(
        session.id,
        call.turn_id,
        draft.content,
        draft.options,
        False,
        question_kind=draft.kind,
        tool_name=request.name,
        target_kind=request.target.kind,
        proposal_change_id=request.target.change_id,
        db_type=request.db_type,
        reset_schema=request.reset_schema,
        expected_revision=request.expected_revision,
        endpoint_risk=prepared.endpoint_risk,
        schema_name=prepared.schema_name,
    )
