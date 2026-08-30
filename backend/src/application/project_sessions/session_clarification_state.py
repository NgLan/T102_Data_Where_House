"""Transactional validation and persistence for clarification answers."""

from dataclasses import dataclass

from src.application.common.unit_of_work import IUnitOfWork
from src.application.project_sessions.clarification_answer import (
    raise_stale_clarification,
    resolve_clarification_answer,
)
from src.application.project_sessions.input import AnswerClarificationInput
from src.application.project_sessions.session_access import (
    OwnedSessionAccess,
    ensure_session_purpose,
)
from src.application.project_sessions.session_event_factory import (
    AnswerEventInput,
    create_agent_call,
    create_answer,
)
from src.application.project_sessions.session_turn_history import TURN_STALE_AFTER
from src.common.utils.datetime import utc_now
from src.domain.project_session.clarification import ClarificationQuestionMetadata
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import SessionEventType, SessionPurpose
from src.domain.project_session.i_project_session_repository import IProjectSessionRepository
from src.domain.project_session.i_session_event_repository import ISessionEventRepository
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ClarificationStateDependencies:
    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    unit_of_work: IUnitOfWork
    access: OwnedSessionAccess


class SessionClarificationState:
    def __init__(self, dependencies: ClarificationStateDependencies) -> None:
        self._dependencies = dependencies

    async def begin(self, data: AnswerClarificationInput) -> tuple[ProjectSession, SessionEvent, SessionEvent, str]:
        deps = self._dependencies
        async with deps.unit_of_work:
            session = await deps.access.require(data.session_id, for_update=True)
            ensure_session_purpose(session, SessionPurpose.DATA_MODELING)
            question = await self.require_question(session, data.question_id)
            content, kind, index = resolve_clarification_answer(question, data)
            if question.turn_id is None:
                raise_stale_clarification()
            session.resume_turn(data.question_id, question.turn_id, utc_now() - TURN_STALE_AFTER)
            answer_data = AnswerEventInput(session.id, question.turn_id, question.id, content, kind, index)
            call = create_agent_call(session.id, question.turn_id)
            await deps.sessions.save(session)
            await deps.events.save(create_answer(answer_data))
            await deps.events.save(call)
            await deps.unit_of_work.commit()
        return session, question, call, content

    async def require_question(self, session: ProjectSession, question_id: EntityID) -> SessionEvent:
        if session.pending_question_id != question_id:
            raise_stale_clarification()
        question = await self._dependencies.events.get_by_id(question_id)
        if not _is_pending_question(session, question):
            raise_stale_clarification()
        return question


def _is_pending_question(session: ProjectSession, question: SessionEvent | None) -> bool:
    return bool(
        question
        and question.session_id == session.id
        and question.type is SessionEventType.QUESTION
        and isinstance(question.metadata, ClarificationQuestionMetadata)
    )
