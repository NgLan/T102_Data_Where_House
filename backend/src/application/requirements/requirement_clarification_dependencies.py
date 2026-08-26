"""Dependency bundle cho Requirement clarification lifecycle."""

from dataclasses import dataclass

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.project_sessions.conversation_summary_compactor import (
    ConversationSummaryCompactor,
)
from src.application.requirements.i_requirement_service import IRequirementAnalysisAgent
from src.application.requirements.requirement_clarification_state import (
    RequirementClarificationStateReader,
)
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.project_session.i_project_session_repository import IProjectSessionRepository
from src.domain.project_session.i_session_event_repository import ISessionEventRepository
from src.domain.requirement.i_requirement_repository import IRequirementRepository
from src.domain.requirement_file.i_requirement_file_repository import (
    IRequirementFileRepository,
)


@dataclass(frozen=True, slots=True)
class RequirementClarificationDependencies:
    """Các port request-scoped dùng chung cho coordinator."""

    projects: IProjectRepository
    requirement_files: IRequirementFileRepository
    requirements: IRequirementRepository
    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    agent: IRequirementAnalysisAgent
    unit_of_work: IUnitOfWork
    access: ProjectAccessPolicy
    context: ConversationSummaryCompactor
    state: RequirementClarificationStateReader
