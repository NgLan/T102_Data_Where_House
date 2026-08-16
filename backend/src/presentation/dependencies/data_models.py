"""Dependency wiring dành riêng cho Data Model application service."""

from typing import Annotated

from config import get_settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.data_models.data_model_service import DataModelService
from src.application.data_models.i_data_model_service import IDataModelService
from src.domain.data_model.generation import IDataModelGenerator
from src.infrastructure.agents.data_model_generator import LangGraphDataModelGenerator
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.llm.factory import build_chat_model
from src.infrastructure.repositories.postgres_analytical_requirement_repository import (
    PostgresAnalyticalRequirementRepository,
)
from src.infrastructure.repositories.postgres_data_model_repository import (
    PostgresDataModelRepository,
)
from src.infrastructure.repositories.postgres_data_source_repository import (
    PostgresDataSourceRepository,
)
from src.infrastructure.repositories.postgres_requirement_repository import (
    PostgresRequirementRepository,
)
from src.infrastructure.security.pii_guard import PiiGuard
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from functools import lru_cache

from src.application.data_models.i_view_ddl_service import IViewDdlService
from src.application.data_models.view_ddl_service import ViewDdlService

def get_pii_guard() -> PiiGuard:
    """Cấp phát bộ che thông tin cá nhân đặt giữa Agent và LLM API (FR6.2)."""
    return PiiGuard(enabled=get_settings().pii_masking_enabled)


def get_data_model_generator(
    pii_guard: Annotated[PiiGuard, Depends(get_pii_guard)],
) -> IDataModelGenerator:
    """Cấp phát pipeline 4 agent sinh mô hình dữ liệu bằng AI."""
    return LangGraphDataModelGenerator(build_chat_model(), pii_guard)


def get_data_model_service(
    generator: Annotated[IDataModelGenerator, Depends(get_data_model_generator)],
    session: AsyncSession = Depends(get_async_db_session),
) -> IDataModelService:
    """Khởi tạo Data Model service và Unit of Work dùng chung session."""
    return DataModelService(
        repository=PostgresDataModelRepository(session),
        unit_of_work=SqlAlchemyUnitOfWork(session),
        requirement_repository=PostgresRequirementRepository(session),
        data_source_repository=PostgresDataSourceRepository(session),
        analytical_repository=PostgresAnalyticalRequirementRepository(session),
        generator=generator,
    )


DataModelServiceDependency = Annotated[
    IDataModelService,
    Depends(get_data_model_service),
]
"""Dependency injection cho các use case Data Model."""


@lru_cache
def get_view_ddl_service() -> IViewDdlService:
    """Khởi tạo và cache service sinh DDL không trạng thái."""
    return ViewDdlService()
