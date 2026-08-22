"""Dependency wiring cho Project application service."""

from typing import Annotated

from config import get_settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.projects.i_project_service import IProjectService
from src.application.projects.project_service import ProjectService
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_data_model_repository import (
    PostgresDataModelRepository,
)
from src.infrastructure.repositories.postgres_data_source_repository import (
    PostgresDataSourceRepository,
)
from src.infrastructure.repositories.postgres_project_member_repository import (
    PostgresProjectMemberRepository,
)
from src.infrastructure.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)
from src.infrastructure.repositories.postgres_requirement_repository import (
    PostgresRequirementRepository,
)
from src.infrastructure.storage.local_storage import LocalFileStorage
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.project_access import ProjectAccessDependency


def get_project_service(
    access: ProjectAccessDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> IProjectService:
    """Khởi tạo Project service cho người dùng và transaction hiện tại."""
    return ProjectService(
        projects=PostgresProjectRepository(session),
        members=PostgresProjectMemberRepository(session),
        data_sources=PostgresDataSourceRepository(session),
        requirements=PostgresRequirementRepository(session),
        data_models=PostgresDataModelRepository(session),
        artifacts=LocalFileStorage(get_settings().upload_dir),
        unit_of_work=SqlAlchemyUnitOfWork(session),
        access=access,
    )


ProjectServiceDependency = Annotated[
    IProjectService,
    Depends(get_project_service),
]
