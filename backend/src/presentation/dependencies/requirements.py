"""Dependency wiring dành riêng cho Requirement application service."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.requirements.i_requirement_service import IRequirementService
from src.application.requirements.requirement_service import RequirementService
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)
from src.infrastructure.repositories.postgres_requirement_repository import (
    PostgresRequirementRepository,
)
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


def get_requirement_service(
    session: AsyncSession = Depends(get_async_db_session),
) -> IRequirementService:
    """Khởi tạo Requirement service và Unit of Work dùng chung session."""
    repository = PostgresRequirementRepository(session)
    project_repository = PostgresProjectRepository(session)
    unit_of_work = SqlAlchemyUnitOfWork(session)
    return RequirementService(repository, project_repository, unit_of_work)


RequirementServiceDependency = Annotated[
    IRequirementService,
    Depends(get_requirement_service),
]
