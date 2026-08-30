"""Coordinates one persisted Agent turn for a project session."""

from dataclasses import dataclass

from src.application.agent_tools import IAgentToolService, parse_agent_tool_intent
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataWarehouseWorkflowService,
)
from src.application.data_warehouse_workflows.input import CreateAgentTurnInput
from src.application.data_warehouse_workflows.output import AgentTurnKind, AgentTurnOutput
from src.application.project_sessions.conversation_context import ConversationInputKind
from src.application.project_sessions.conversation_context_policy import (
    ConversationMemoryInput,
)
from src.application.project_sessions.conversation_summary_compactor import ConversationSummaryCompactor
from src.application.project_sessions.input import SendSessionMessageInput
from src.application.project_sessions.output import SessionTurnOutput
from src.application.project_sessions.session_access import OwnedSessionAccess
from src.application.project_sessions.session_tool_coordinator import (
    SessionToolCoordinator,
    SessionToolDependencies,
)
from src.application.project_sessions.session_turn_completion import (
    SessionTurnCompletion,
    TurnCompletionDependencies,
)
from src.application.project_sessions.session_turn_starter import (
    SessionTurnStartDependencies,
    SessionTurnStarter,
)
from src.application.project_sessions.structured_tool_intent import (
    StructuredToolIntentInput,
    create_structured_tool_intent,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.i_project_session_repository import (
    IProjectSessionRepository,
)
from src.domain.project_session.i_session_event_repository import (
    ISessionEventRepository,
)


@dataclass(frozen=True, slots=True)
class SessionTurnDependencies:
    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    workflow: IDataWarehouseWorkflowService
    unit_of_work: IUnitOfWork
    access: OwnedSessionAccess
    context: ConversationSummaryCompactor
    tools: IAgentToolService | None = None


@dataclass(frozen=True, slots=True)
class StructuredToolTurn:
    data: SendSessionMessageInput
    session: ProjectSession
    call: SessionEvent
    result: AgentTurnOutput


class SessionTurnCoordinator:
    def __init__(self, dependencies: SessionTurnDependencies) -> None:
        self._dependencies = dependencies
        self._starter = _build_starter(dependencies)
        self._completion = _build_completion(dependencies)
        self._tools = _build_tools(dependencies)

    async def send(self, data: SendSessionMessageInput) -> SessionTurnOutput:
        session, call = await self._starter.begin(data)
        try:
            return await self._continue(data, session, call)
        except Exception:
            await self._completion.fail(session, call)
            raise

    async def _continue(
        self,
        data: SendSessionMessageInput,
        session: ProjectSession,
        call: SessionEvent,
    ) -> SessionTurnOutput:
        intent = parse_agent_tool_intent(session.project_id, data.content, data.locale) if self._tools else None
        if intent is not None and self._tools is not None:
            return await self._tools.start(session, call, intent)
        result = await self._run_agent(session, call, data.content)
        if result.kind is AgentTurnKind.TOOL_REQUEST:
            return await self._start_structured_tool(StructuredToolTurn(data, session, call, result))
        output = await self._completion.complete(session, call, result)
        await self._dependencies.context.compact_after_completion(session.id, session.project_id)
        return output

    async def _start_structured_tool(self, turn: StructuredToolTurn) -> SessionTurnOutput:
        data, session, call, result = (turn.data, turn.session, turn.call, turn.result)
        if self._tools is None or result.tool_request is None:
            raise BusinessException(ErrorCode.VALIDATION_ERROR, "Agent tool request không hợp lệ.")
        tool_input = StructuredToolIntentInput(session.project_id, data.content, data.locale, result.tool_request)
        return await self._tools.start(session, call, create_structured_tool_intent(tool_input))

    async def _run_agent(self, session: ProjectSession, call: SessionEvent, content: str) -> AgentTurnOutput:
        memory = await self._dependencies.context.build_memory(
            ConversationMemoryInput(
                session.id,
                session.project_id,
                content,
                ConversationInputKind.USER_MESSAGE,
            )
        )
        return await self._dependencies.workflow.create_agent_turn(
            CreateAgentTurnInput(
                session.project_id,
                content,
                memory,
                turn_id=call.turn_id,
            )
        )


def _build_starter(data: SessionTurnDependencies) -> SessionTurnStarter:
    dependencies = SessionTurnStartDependencies(data.sessions, data.events, data.unit_of_work, data.access)
    return SessionTurnStarter(dependencies)


def _build_completion(data: SessionTurnDependencies) -> SessionTurnCompletion:
    dependencies = TurnCompletionDependencies(data.sessions, data.events, data.unit_of_work)
    return SessionTurnCompletion(dependencies)


def _build_tools(data: SessionTurnDependencies) -> SessionToolCoordinator | None:
    if data.tools is None:
        return None
    dependencies = SessionToolDependencies(data.sessions, data.events, data.unit_of_work, data.tools)
    return SessionToolCoordinator(dependencies)
