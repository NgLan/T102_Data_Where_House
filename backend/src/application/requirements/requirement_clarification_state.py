"""Dẫn xuất Requirement clarification UI state từ canonical persistence."""

from dataclasses import dataclass

from src.application.project_sessions.clarification_output import ClarificationQuestionOutput
from src.application.project_sessions.output import ProjectSessionOutput
from src.application.requirements.output import (
    RequirementClarificationStateOutput,
    RequirementOutput,
)
from src.domain.project.entities import Project
from src.domain.project_session.clarification import ClarificationQuestionMetadata
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import (
    RequirementClarificationStatus,
    RequirementContinuationState,
    SessionEventType,
    SessionPurpose,
    SessionStatus,
)
from src.domain.project_session.i_project_session_repository import IProjectSessionRepository
from src.domain.project_session.i_session_event_repository import ISessionEventRepository
from src.domain.requirement.i_requirement_repository import IRequirementRepository


@dataclass(frozen=True, slots=True)
class RequirementStateDependencies:
    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    requirements: IRequirementRepository


class RequirementClarificationStateReader:
    """Đọc cycle hiện hành; cycle cũ vẫn giữ nguyên cho audit."""

    def __init__(self, dependencies: RequirementStateDependencies) -> None:
        self._dependencies = dependencies

    async def read(self, project: Project) -> RequirementClarificationStateOutput:
        session = await self._current_session(project)
        pending = await self._pending(session)
        requirements = await self._dependencies.requirements.list_by_project(project.id)
        return RequirementClarificationStateOutput(
            ProjectSessionOutput.from_domain(session) if session else None,
            _status(project, session),
            pending,
            tuple(RequirementOutput.from_domain(item) for item in requirements),
            project.requirement_revision,
            project.analyzed_requirement_revision,
            project.is_requirement_analysis_outdated(),
            (
                session.requirement_continuation_state
                if session
                else RequirementContinuationState.NOT_REQUIRED
            ),
        )

    async def _current_session(self, project: Project) -> ProjectSession | None:
        sessions = await self._dependencies.sessions.list_by_project(project.id)
        matching = [
            item
            for item in sessions
            if item.purpose is SessionPurpose.REQUIREMENT_CLARIFICATION
            and item.base_requirement_revision == project.requirement_revision
        ]
        return max(matching, key=lambda item: item.updated_at, default=None)

    async def _pending(
        self, session: ProjectSession | None
    ) -> ClarificationQuestionOutput | None:
        if session is None or session.pending_question_id is None:
            return None
        event = await self._dependencies.events.get_by_id(session.pending_question_id)
        if not _is_pending_question(session, event):
            return None
        return ClarificationQuestionOutput.from_domain(event)


def _status(
    project: Project, session: ProjectSession | None
) -> RequirementClarificationStatus:
    if session is None:
        return RequirementClarificationStatus.IDLE
    if session.status is SessionStatus.ARCHIVED:
        return RequirementClarificationStatus.IDLE
    if session.active_turn_id:
        return RequirementClarificationStatus.PROCESSING
    if session.pending_question_id:
        return RequirementClarificationStatus.NEEDS_CLARIFICATION
    if project.analyzed_requirement_revision == project.requirement_revision:
        return RequirementClarificationStatus.READY
    return RequirementClarificationStatus.IDLE


def _is_pending_question(
    session: ProjectSession, event: SessionEvent | None
) -> bool:
    return bool(
        event
        and event.session_id == session.id
        and event.type is SessionEventType.QUESTION
        and isinstance(event.metadata, ClarificationQuestionMetadata)
    )
