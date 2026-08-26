"""Composition root cho Project Session service."""

from typing import Annotated

from config import get_settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.project_sessions.conversation_canonical_index import (
    CanonicalIndexDependencies,
    ConversationCanonicalIndexReader,
)
from src.application.project_sessions.conversation_context_policy import (
    ConversationContextPolicy,
)
from src.application.project_sessions.conversation_summary_compactor import (
    ConversationSummaryCompactor,
    SummaryCompactorDependencies,
)
from src.application.project_sessions.i_project_session_service import IProjectSessionService
from src.application.project_sessions.project_session_service import (
    ProjectSessionDependencies,
    ProjectSessionService,
)
from src.infrastructure.agents.conversation_summary_agent import ConversationSummaryAgent
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.llm.factory import get_cached_summary_chat_model
from src.infrastructure.repositories.postgres_analytical_requirement_repository import (
    PostgresAnalyticalRequirementRepository,
)
from src.infrastructure.repositories.postgres_data_model_repository import (
    PostgresDataModelRepository,
)
from src.infrastructure.repositories.postgres_data_source_repository import (
    PostgresDataSourceRepository,
)
from src.infrastructure.repositories.postgres_project_session_repository import PostgresProjectSessionRepository
from src.infrastructure.repositories.postgres_requirement_repository import (
    PostgresRequirementRepository,
)
from src.infrastructure.repositories.postgres_session_event_repository import PostgresSessionEventRepository
from src.infrastructure.security.pii_guard import PiiGuard
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.data_model_resources import get_pii_guard
from src.presentation.dependencies.data_warehouse_workflows import DataWarehouseWorkflowDependency
from src.presentation.dependencies.project_access import ProjectAccessDependency


def get_project_session_service(
    workflow: DataWarehouseWorkflowDependency,
    access: ProjectAccessDependency,
    pii_guard: Annotated[PiiGuard, Depends(get_pii_guard)],
    session: AsyncSession = Depends(get_async_db_session),
) -> IProjectSessionService:
    """Nối repositories và workflow bằng cùng request-scoped session."""
    sessions = PostgresProjectSessionRepository(session)
    events = PostgresSessionEventRepository(session)
    unit_of_work = SqlAlchemyUnitOfWork(session)
    context = build_conversation_context(session, pii_guard)
    return ProjectSessionService(
        ProjectSessionDependencies(
            sessions,
            events,
            workflow,
            unit_of_work,
            access,
            context,
        )
    )


def build_conversation_context(
    session: AsyncSession,
    pii_guard: PiiGuard,
) -> ConversationSummaryCompactor:
    """Dựng conversation compactor dùng chung cho mọi session purpose."""
    settings = get_settings()
    sessions = PostgresProjectSessionRepository(session)
    events = PostgresSessionEventRepository(session)
    unit_of_work = SqlAlchemyUnitOfWork(session)
    canonical = ConversationCanonicalIndexReader(
        CanonicalIndexDependencies(
            PostgresRequirementRepository(session),
            PostgresAnalyticalRequirementRepository(session),
            PostgresDataSourceRepository(session),
            PostgresDataModelRepository(session),
        )
    )
    return ConversationSummaryCompactor(
        SummaryCompactorDependencies(
            sessions,
            events,
            ConversationSummaryAgent(get_cached_summary_chat_model, pii_guard),
            canonical,
            unit_of_work,
            ConversationContextPolicy(
                settings.conversation_recent_turns,
                settings.conversation_summary_batch_size,
            ),
        )
    )


ProjectSessionServiceDependency = Annotated[
    IProjectSessionService,
    Depends(get_project_session_service),
]
