"""Acquire a Requirement clarification answer turn atomically."""

from src.application.project_sessions.clarification_answer import (
    raise_stale_clarification,
    resolve_clarification_answer,
)
from src.application.project_sessions.input import AnswerClarificationInput
from src.application.project_sessions.session_event_factory import (
    AgentCallEventInput,
    AnswerEventInput,
    create_answer,
    create_typed_agent_call,
)
from src.application.project_sessions.session_turn_history import TURN_STALE_AFTER
from src.application.requirements.input import AnswerRequirementClarificationInput
from src.application.requirements.requirement_clarification_dependencies import (
    RequirementClarificationDependencies,
)
from src.application.requirements.requirement_clarification_turn_start import (
    RequirementTurnStart,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.datetime import utc_now
from src.domain.project.entities import Project
from src.domain.project_session.clarification import ClarificationQuestionMetadata
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import AgentType, SessionEventType, SessionPurpose
from src.domain.shared.types import EntityID


class RequirementClarificationAnswerTurn:
    """Validate pending question, persist ANSWER and acquire its Agent turn."""

    def __init__(self, dependencies: RequirementClarificationDependencies) -> None:
        self._dependencies = dependencies

    async def start(
        self, data: AnswerRequirementClarificationInput
    ) -> RequirementTurnStart:
        dependencies = self._dependencies
        async with dependencies.unit_of_work:
            project = await dependencies.access.require_owner_for_update(data.project_id)
            session = await dependencies.sessions.get_by_id_for_update(data.session_id)
            _ensure_session(project, session)
            question = await self._question(session, data.question_id)
            content, answer_event = _resolve_answer(session, question, data)
            session.resume_turn(
                question.id, question.turn_id, utc_now() - TURN_STALE_AFTER
            )
            call = _requirement_agent_call(session.id, question.turn_id)
            await dependencies.sessions.save(session)
            await dependencies.events.save(answer_event)
            await dependencies.events.save(call)
            await dependencies.unit_of_work.commit()
        return RequirementTurnStart(
            session, call, question, content, requires_continuation_decision=True
        )

    async def _question(
        self, session: ProjectSession, question_id: EntityID
    ) -> SessionEvent:
        if session.pending_question_id != question_id:
            raise_stale_clarification()
        question = await self._dependencies.events.get_by_id(question_id)
        if not _valid_question(session, question):
            raise_stale_clarification()
        return question


def _resolve_answer(
    session: ProjectSession,
    question: SessionEvent,
    data: AnswerRequirementClarificationInput,
) -> tuple[str, SessionEvent]:
    answer = AnswerClarificationInput(
        session.id, question.id, data.option_index, data.custom_answer
    )
    content, kind, option_index = resolve_clarification_answer(question, answer)
    if question.turn_id is None:
        raise_stale_clarification()
    event = create_answer(
        AnswerEventInput(
            session.id, question.turn_id, question.id, content, kind, option_index
        )
    )
    return content, event


def _requirement_agent_call(session_id: EntityID, turn_id: EntityID) -> SessionEvent:
    return create_typed_agent_call(
        AgentCallEventInput(
            session_id,
            turn_id,
            AgentType.REQUIREMENT,
            "requirement-clarification",
        )
    )


def _ensure_session(project: Project, session: ProjectSession | None) -> None:
    if session is None:
        raise BusinessException(ErrorCode.SESSION_NOT_FOUND, "Session không tồn tại.")
    if session.project_id != project.id or session.purpose is not SessionPurpose.REQUIREMENT_CLARIFICATION:
        raise BusinessException(ErrorCode.SESSION_PURPOSE_MISMATCH, "Sai Requirement session.")
    expected = session.base_requirement_revision
    if expected is None or project.requirement_revision != expected:
        raise BusinessException(
            ErrorCode.REQUIREMENT_REVISION_CONFLICT,
            "Requirement revision không còn hiện hành.",
        )


def _valid_question(session: ProjectSession, question: SessionEvent | None) -> bool:
    return bool(
        question
        and question.session_id == session.id
        and question.type is SessionEventType.QUESTION
        and isinstance(question.metadata, ClarificationQuestionMetadata)
    )
