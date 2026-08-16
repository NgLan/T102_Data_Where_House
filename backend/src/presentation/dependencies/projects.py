"""Dependency wiring cho Project application service."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.projects.i_project_service import IProjectService
from src.application.projects.project_service import (
    ProjectService,
    ProjectServiceDependencies,
)
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_data_source_repository import (
    PostgresDataSourceRepository,
)
from src.infrastructure.repositories.postgres_project_member_repository import (
    PostgresProjectMemberRepository,
)
from src.infrastructure.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)
from src.infrastructure.storage.local_project_artifact_store import (
    LocalProjectArtifactStore,
)
from src.infrastructure.storage.local_storage import LocalFileStorage
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.auth import CurrentUserDependency


def get_project_service(
    current_user: CurrentUserDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> IProjectService:
    """Khởi tạo Project service cho người dùng và transaction hiện tại."""
    dependencies = ProjectServiceDependencies(
        projects=PostgresProjectRepository(session),
        members=PostgresProjectMemberRepository(session),
        data_sources=PostgresDataSourceRepository(session),
        artifacts=LocalProjectArtifactStore(LocalFileStorage()),
        unit_of_work=SqlAlchemyUnitOfWork(session),
    )
    return ProjectService(dependencies, actor_id=current_user.id)


ProjectServiceDependency = Annotated[
    IProjectService,
    Depends(get_project_service),
]
