"""Dependency wiring cho Requirement File application service."""

from typing import Annotated

from config import get_settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.requirement_files.i_requirement_file_service import (
    IRequirementFileService,
)
from src.application.requirement_files.requirement_file_service import (
    RequirementFileService,
)
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.parsers.requirement_document_parser import (
    RequirementDocumentParser,
)
from src.infrastructure.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)
from src.infrastructure.repositories.postgres_requirement_file_repository import (
    PostgresRequirementFileRepository,
)
from src.infrastructure.storage.local_storage import LocalFileStorage
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.project_access import ProjectAccessDependency


def get_requirement_file_service(
    access: ProjectAccessDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> IRequirementFileService:
    """Dựng Requirement File service cho request hiện hành."""
    return RequirementFileService(
        files=PostgresRequirementFileRepository(session),
        storage=LocalFileStorage(get_settings().upload_dir),
        parser=RequirementDocumentParser(),
        projects=PostgresProjectRepository(session),
        unit_of_work=SqlAlchemyUnitOfWork(session),
        access=access,
    )


RequirementFileServiceDependency = Annotated[
    IRequirementFileService, Depends(get_requirement_file_service)
]
