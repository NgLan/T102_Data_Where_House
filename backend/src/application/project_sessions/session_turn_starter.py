"""Transactional persistence of the first events in a session turn."""

from dataclasses import dataclass

from src.application.common.unit_of_work import IUnitOfWork
from src.application.project_sessions.input import SendSessionMessageInput
from src.application.project_sessions.session_access import (
    OwnedSessionAccess,
    ensure_session_purpose,
)
from src.application.project_sessions.session_event_factory import (
    UserEventInput,
    create_agent_call,
    create_user_event,
)
from src.application.project_sessions.session_turn_history import (
    TURN_STALE_AFTER,
    create_stale_turn_event,
)
from src.common.utils.datetime import utc_now
from src.common.utils.uuid import generate_uuid
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import SessionPurpose
from src.domain.project_session.i_project_session_repository import IProjectSessionRepository
from src.domain.project_session.i_session_event_repository import ISessionEventRepository


@dataclass(frozen=True, slots=True)
class SessionTurnStartDependencies:
    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    unit_of_work: IUnitOfWork
    access: OwnedSessionAccess


class SessionTurnStarter:
    def __init__(self, dependencies: SessionTurnStartDependencies) -> None:
        self._dependencies = dependencies

    async def begin(self, data: SendSessionMessageInput) -> tuple[ProjectSession, SessionEvent]:
        deps = self._dependencies
        async with deps.unit_of_work:
            session = await deps.access.require(data.session_id, for_update=True)
            ensure_session_purpose(session, SessionPurpose.DATA_MODELING)
            history = await deps.events.list_by_session(session.id, limit=200)
            call = await self._persist(session, data, history)
            await deps.unit_of_work.commit()
        return session, call

    async def _persist(
        self,
        session: ProjectSession,
        data: SendSessionMessageInput,
        history: list[SessionEvent],
    ) -> SessionEvent:
        turn_id = generate_uuid()
        stale_event = create_stale_turn_event(session, history)
        session.acquire_turn(turn_id, utc_now() - TURN_STALE_AFTER)
        call = create_agent_call(session.id, turn_id)
        await self._dependencies.sessions.save(session)
        if stale_event:
            await self._dependencies.events.save(stale_event)
        user_input = UserEventInput(session.id, turn_id, data.content, data.client_message_id)
        await self._dependencies.events.save(create_user_event(user_input))
        await self._dependencies.events.save(call)
        return call
