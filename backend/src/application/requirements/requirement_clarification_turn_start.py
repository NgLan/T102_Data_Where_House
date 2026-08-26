"""Acquire turn và persist input events trước khi gọi RequirementAgent."""

from dataclasses import dataclass

from src.application.project_sessions.session_event_factory import (
    AgentCallEventInput,
    create_typed_agent_call,
    create_user_event,
)
from src.application.project_sessions.session_event_inputs import UserEventInput
from src.application.project_sessions.session_turn_history import TURN_STALE_AFTER
from src.application.requirements.input import (
    AnalyzeRequirementClarificationInput,
    SendRequirementClarificationMessageInput,
)
from src.application.requirements.requirement_clarification_dependencies import (
    RequirementClarificationDependencies,
)
from src.application.requirements.requirement_clarification_guards import (
    ensure_requirement_message_session,
    ensure_requirement_revision,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.datetime import utc_now
from src.common.utils.uuid import generate_uuid
from src.domain.project.entities import Project
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import AgentType, SessionPurpose
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class RequirementTurnStart:
    session: ProjectSession
    call: SessionEvent
    question: SessionEvent | None = None
    current_input: str | None = None
    requires_continuation_decision: bool = False


class RequirementClarificationTurnStarter:
    """Serialize analyze/answer bằng Project row lock và session turn lock."""

    def __init__(self, dependencies: RequirementClarificationDependencies) -> None:
        self._dependencies = dependencies

    async def analyze(
        self, data: AnalyzeRequirementClarificationInput
    ) -> RequirementTurnStart:
        dependencies = self._dependencies
        async with dependencies.unit_of_work:
            project = await dependencies.access.require_owner_for_update(data.project_id)
            ensure_requirement_revision(project, data.expected_revision)
            await self._ensure_context(project)
            session = await self._current_or_new(project)
            call = await self._acquire(session, generate_uuid())
            await dependencies.unit_of_work.commit()
        return RequirementTurnStart(session, call)

    async def message(
        self, data: SendRequirementClarificationMessageInput
    ) -> RequirementTurnStart:
        """Persist user message và acquire một follow-up turn độc lập."""
        dependencies = self._dependencies
        async with dependencies.unit_of_work:
            project = await dependencies.access.require_owner_for_update(data.project_id)
            ensure_requirement_revision(project, data.expected_revision)
            session = await dependencies.sessions.get_by_id_for_update(data.session_id)
            ensure_requirement_message_session(project, session)
            turn_id = generate_uuid()
            call = await self._acquire(session, turn_id)
            await dependencies.events.save(
                create_user_event(UserEventInput(session.id, turn_id, data.message))
            )
            await dependencies.unit_of_work.commit()
        return RequirementTurnStart(
            session, call, current_input=data.message, requires_continuation_decision=True
        )

    async def _current_or_new(self, project: Project) -> ProjectSession:
        dependencies = self._dependencies
        session = await dependencies.sessions.get_active_by_project_purpose_for_update(
            project.id, SessionPurpose.REQUIREMENT_CLARIFICATION
        )
        if session and session.base_requirement_revision != project.requirement_revision:
            session.archive()
            await dependencies.sessions.save(session)
            session = None
        return session or ProjectSession(
            project_id=project.id,
            user_id=dependencies.access.actor_id,
            title="Requirement Clarification",
            purpose=SessionPurpose.REQUIREMENT_CLARIFICATION,
            base_requirement_revision=project.requirement_revision,
        )

    async def _acquire(
        self, session: ProjectSession, turn_id: EntityID
    ) -> SessionEvent:
        session.acquire_turn(turn_id, utc_now() - TURN_STALE_AFTER)
        call = create_typed_agent_call(
            AgentCallEventInput(
                session.id,
                turn_id,
                AgentType.REQUIREMENT,
                "requirement-clarification",
            )
        )
        await self._dependencies.sessions.save(session)
        await self._dependencies.events.save(call)
        return call

    async def _ensure_context(self, project: Project) -> None:
        files = await self._dependencies.requirement_files.list_by_project(project.id)
        if not (project.requirement or "").strip() and not files:
            raise BusinessException(
                ErrorCode.REQUIREMENT_CONTEXT_EMPTY,
                "Cần Raw Requirement hoặc ít nhất một Requirement Document.",
            )
