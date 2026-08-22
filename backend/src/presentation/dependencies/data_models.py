"""Composition root dành riêng cho Data Model service."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.data_models.data_model_service import DataModelService
from src.application.data_models.i_data_model_service import IDataModelService
from src.infrastructure.codegen.pydbml_ddl_generator import PyDbmlDdlGenerator
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_data_model_change_repository import (
    PostgresDataModelChangeRepository,
)
from src.infrastructure.repositories.postgres_data_model_repository import PostgresDataModelRepository
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.data_model_resources import get_validation_engine
from src.presentation.dependencies.project_access import ProjectAccessDependency


def get_data_model_service(
    access: ProjectAccessDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> IDataModelService:
    """Wiring DataModelService không phụ thuộc Agent implementation."""
    return DataModelService(
        models=PostgresDataModelRepository(session),
        changes=PostgresDataModelChangeRepository(session),
        validator=get_validation_engine(),
        unit_of_work=SqlAlchemyUnitOfWork(session),
        access=access,
        ddl_generator=PyDbmlDdlGenerator(),
    )


DataModelServiceDependency = Annotated[IDataModelService, Depends(get_data_model_service)]
