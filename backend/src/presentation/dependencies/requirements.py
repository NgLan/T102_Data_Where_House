"""Dependency wiring dành riêng cho Requirement application service."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.requirements.i_requirement_service import IRequirementService
from src.application.requirements.requirement_clarification_coordinator import (
    RequirementClarificationCoordinator,
)
from src.application.requirements.requirement_clarification_dependencies import (
    RequirementClarificationDependencies,
)
from src.application.requirements.requirement_clarification_state import (
    RequirementClarificationStateReader,
    RequirementStateDependencies,
)
from src.application.requirements.requirement_continuation_coordinator import (
    RequirementContinuationCoordinator,
)
from src.application.requirements.requirement_service import RequirementService
from src.infrastructure.agents.requirement_analysis_agent import RequirementAnalysisAgent
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.llm.factory import get_cached_chat_model
from src.infrastructure.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)
from src.infrastructure.repositories.postgres_project_session_repository import (
    PostgresProjectSessionRepository,
)
from src.infrastructure.repositories.postgres_requirement_file_repository import (
    PostgresRequirementFileRepository,
)
from src.infrastructure.repositories.postgres_requirement_repository import (
    PostgresRequirementRepository,
)
from src.infrastructure.repositories.postgres_session_event_repository import (
    PostgresSessionEventRepository,
)
from src.infrastructure.security.pii_guard import PiiGuard
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.data_model_resources import get_pii_guard
from src.presentation.dependencies.project_access import ProjectAccessDependency
from src.presentation.dependencies.project_sessions import build_conversation_context


def get_requirement_service(
    access: ProjectAccessDependency,
    pii_guard: Annotated[PiiGuard, Depends(get_pii_guard)],
    session: AsyncSession = Depends(get_async_db_session),
) -> IRequirementService:
    """Khởi tạo Requirement service và Unit of Work dùng chung session."""
    projects = PostgresProjectRepository(session)
    requirements = PostgresRequirementRepository(session)
    sessions = PostgresProjectSessionRepository(session)
    events = PostgresSessionEventRepository(session)
    state = RequirementClarificationStateReader(
        RequirementStateDependencies(sessions, events, requirements)
    )
    dependencies = RequirementClarificationDependencies(
        projects,
        PostgresRequirementFileRepository(session),
        requirements,
        sessions,
        events,
        RequirementAnalysisAgent(get_cached_chat_model, pii_guard),
        SqlAlchemyUnitOfWork(session),
        access,
        build_conversation_context(session, pii_guard),
        state,
    )
    return RequirementService(
        requirements,
        access,
        RequirementClarificationCoordinator(dependencies),
        RequirementContinuationCoordinator(dependencies),
    )


RequirementServiceDependency = Annotated[
    IRequirementService,
    Depends(get_requirement_service),
]
