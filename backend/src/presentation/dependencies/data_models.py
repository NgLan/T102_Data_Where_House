"""Dependency wiring dành riêng cho Data Model application service."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.data_models.data_model_service import DataModelService
from src.application.data_models.i_data_model_service import IDataModelService
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_data_model_repository import (
    PostgresDataModelRepository,
)
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from functools import lru_cache

from src.application.data_models.i_view_ddl_service import IViewDdlService
from src.application.data_models.view_ddl_service import ViewDdlService

def get_data_model_service(
    session: AsyncSession = Depends(get_async_db_session),
) -> IDataModelService:
    """Khởi tạo Data Model service và Unit of Work dùng chung session."""
    repository = PostgresDataModelRepository(session)
    unit_of_work = SqlAlchemyUnitOfWork(session)
    return DataModelService(repository, unit_of_work)


DataModelServiceDependency = Annotated[
    IDataModelService,
    Depends(get_data_model_service),
]
"""Dependency injection cho các use case Data Model."""


@lru_cache
def get_view_ddl_service() -> IViewDdlService:
    """Khởi tạo và cache service sinh DDL không trạng thái."""
    return ViewDdlService()
