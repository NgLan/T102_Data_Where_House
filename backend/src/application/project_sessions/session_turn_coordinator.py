"""Coordinates one persisted Agent turn for a project session."""

from dataclasses import dataclass

from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataWarehouseWorkflowService,
)
from src.application.data_warehouse_workflows.input import CreateAgentTurnInput
from src.application.data_warehouse_workflows.output import AgentTurnOutput
from src.application.project_sessions.conversation_context import ConversationInputKind
from src.application.project_sessions.conversation_context_policy import (
    ConversationMemoryInput,
)
from src.application.project_sessions.conversation_summary_compactor import ConversationSummaryCompactor
from src.application.project_sessions.input import SendSessionMessageInput
from src.application.project_sessions.output import SessionTurnOutput
from src.application.project_sessions.session_access import (
    OwnedSessionAccess,
    ensure_session_purpose,
)
from src.application.project_sessions.session_event_factory import (
    UserEventInput,
    create_agent_call,
    create_user_event,
)
from src.application.project_sessions.session_turn_completion import (
    SessionTurnCompletion,
    TurnCompletionDependencies,
)
from src.application.project_sessions.session_turn_history import TURN_STALE_AFTER, create_stale_turn_event
from src.common.utils.datetime import utc_now
from src.common.utils.uuid import generate_uuid
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import SessionPurpose
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


class SessionTurnCoordinator:
    def __init__(self, dependencies: SessionTurnDependencies) -> None:
        self._dependencies = dependencies
        self._completion = SessionTurnCompletion(
            TurnCompletionDependencies(
                dependencies.sessions,
                dependencies.events,
                dependencies.unit_of_work,
            )
        )

    async def send(self, data: SendSessionMessageInput) -> SessionTurnOutput:
        session, call = await self._begin(data)
        try:
            result = await self._run_agent(session, call, data.content)
        except Exception:
            await self._completion.fail(session, call)
            raise
        output = await self._completion.complete(session, call, result)
        await self._dependencies.context.compact_after_completion(
            session.id, session.project_id
        )
        return output

    async def _run_agent(
        self, session: ProjectSession, call: SessionEvent, content: str
    ) -> AgentTurnOutput:
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

    async def _begin(self, data: SendSessionMessageInput) -> tuple[ProjectSession, SessionEvent]:
        dependencies = self._dependencies
        async with dependencies.unit_of_work:
            session = await dependencies.access.require(data.session_id, for_update=True)
            ensure_session_purpose(session, SessionPurpose.DATA_MODELING)
            history = await dependencies.events.list_by_session(session.id, limit=200)
            call = await self._persist_start(session, data.content, history)
            await dependencies.unit_of_work.commit()
        return session, call

    async def _persist_start(
        self,
        session: ProjectSession,
        content: str,
        history: list[SessionEvent],
    ) -> SessionEvent:
        turn_id = generate_uuid()
        stale_event = create_stale_turn_event(session, history)
        session.acquire_turn(turn_id, utc_now() - TURN_STALE_AFTER)
        call = create_agent_call(session.id, turn_id)
        await self._dependencies.sessions.save(session)
        if stale_event:
            await self._dependencies.events.save(stale_event)
        await self._dependencies.events.save(create_user_event(UserEventInput(session.id, turn_id, content)))
        await self._dependencies.events.save(call)
        return call
