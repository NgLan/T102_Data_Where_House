"""Transactional writer shared by Agent tool state-machine steps."""

from dataclasses import dataclass

from src.application.common.unit_of_work import IUnitOfWork
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.i_project_session_repository import IProjectSessionRepository
from src.domain.project_session.i_session_event_repository import ISessionEventRepository


@dataclass(frozen=True, slots=True)
class ToolEventWriterDependencies:
    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    unit_of_work: IUnitOfWork


class SessionToolEventWriter:
    def __init__(self, dependencies: ToolEventWriterDependencies) -> None:
        self._dependencies = dependencies

    async def persist(self, session: ProjectSession, events: tuple[SessionEvent, ...]) -> None:
        dependencies = self._dependencies
        async with dependencies.unit_of_work:
            for event in events:
                await dependencies.events.save(event)
            await dependencies.sessions.save(session)
            await dependencies.unit_of_work.commit()
