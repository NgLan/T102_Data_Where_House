"""Persisted confirmation state machine for allowlisted Agent tools."""

from dataclasses import dataclass, replace

from src.application.agent_tools import AgentToolIntent, IAgentToolService
from src.application.common.unit_of_work import IUnitOfWork
from src.application.project_sessions.output import SessionTurnOutput
from src.application.project_sessions.session_tool_event_writer import (
    SessionToolEventWriter,
    ToolEventWriterDependencies,
)
from src.application.project_sessions.session_tool_execution import (
    SessionToolExecution,
    ToolExecutionDependencies,
)
from src.application.project_sessions.session_tool_payloads import (
    request_from_question,
    require_tool_question,
)
from src.application.project_sessions.session_tool_questions import (
    SessionToolQuestionWriter,
    ToolQuestionDependencies,
)
from src.domain.project_session.clarification import ClarificationQuestionMetadata
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import SessionQuestionKind
from src.domain.project_session.i_project_session_repository import IProjectSessionRepository
from src.domain.project_session.i_session_event_repository import ISessionEventRepository


@dataclass(frozen=True, slots=True)
class SessionToolDependencies:
    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    unit_of_work: IUnitOfWork
    tools: IAgentToolService


@dataclass(frozen=True, slots=True)
class ToolResumeInput:
    session: ProjectSession
    question: SessionEvent
    call: SessionEvent
    option_index: int | None


class SessionToolCoordinator:
    """Routes only valid persisted state transitions; LLM output cannot bypass it."""

    def __init__(self, dependencies: SessionToolDependencies) -> None:
        writer = SessionToolEventWriter(
            ToolEventWriterDependencies(dependencies.sessions, dependencies.events, dependencies.unit_of_work)
        )
        question_dependencies = ToolQuestionDependencies(writer)
        execution_dependencies = ToolExecutionDependencies(dependencies.tools, writer)
        self._tools = dependencies.tools
        self._questions = SessionToolQuestionWriter(question_dependencies)
        self._execution = SessionToolExecution(execution_dependencies)

    async def start(self, session: ProjectSession, call: SessionEvent, intent: AgentToolIntent) -> SessionTurnOutput:
        if not intent.requires_confirmation:
            return await self._execution.execute(session, call, intent.request)
        prepared = await self._tools.prepare(intent.request)
        if not prepared.ready:
            return await self._execution.complete_unready(session, call, prepared)
        if prepared.request.reset_schema is None:
            return await self._questions.ask_mode(session, call, prepared)
        return await self._questions.ask_confirmation(session, call, prepared)

    async def resume(self, data: ToolResumeInput) -> SessionTurnOutput:
        metadata = require_tool_question(data.question)
        if data.option_index is None:
            return await self._execution.cancel(data.session, data.call)
        if metadata.question_kind is SessionQuestionKind.SANDBOX_MODE_SELECTION:
            return await self._resume_mode(data, metadata)
        if metadata.question_kind is SessionQuestionKind.TOOL_CONFIRMATION:
            if data.option_index != 0:
                return await self._execution.cancel(data.session, data.call)
            return await self._execution.execute(
                data.session,
                data.call,
                request_from_question(data.session, metadata),
            )
        raise ValueError("Question is not an Agent tool action.")

    async def _resume_mode(self, data: ToolResumeInput, metadata: ClarificationQuestionMetadata) -> SessionTurnOutput:
        if data.option_index == 2:
            return await self._execution.cancel(data.session, data.call)
        request = replace(
            request_from_question(data.session, metadata),
            reset_schema=data.option_index == 1,
        )
        prepared = await self._tools.prepare(request)
        if not prepared.ready:
            return await self._execution.complete_unready(data.session, data.call, prepared)
        return await self._questions.ask_confirmation(data.session, data.call, prepared)
