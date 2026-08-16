"""Dependency wiring cho Data Source application service."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.data_sources.data_source_service import (
    DataSourceService,
    DataSourceServiceDependencies,
)
from src.application.data_sources.i_data_source_service import IDataSourceService
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_data_source_repository import PostgresDataSourceRepository
from src.infrastructure.repositories.postgres_project_member_repository import PostgresProjectMemberRepository
from src.infrastructure.repositories.postgres_project_repository import PostgresProjectRepository
from src.infrastructure.storage.file_parser_service_impl import FileParserServiceImpl
from src.infrastructure.storage.local_storage import LocalFileStorage
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.auth import CurrentUserDependency


def get_data_source_service(
    current_user: CurrentUserDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> IDataSourceService:
    """Khởi tạo service với actor và transaction của request hiện tại."""
    dependencies = DataSourceServiceDependencies(
        projects=PostgresProjectRepository(session),
        members=PostgresProjectMemberRepository(session),
        sources=PostgresDataSourceRepository(session),
        files=LocalFileStorage(),
        parser=FileParserServiceImpl(),
        unit_of_work=SqlAlchemyUnitOfWork(session),
    )
    return DataSourceService(dependencies, actor_id=current_user.id)


DataSourceServiceDependency = Annotated[
    IDataSourceService,
    Depends(get_data_source_service),
]
