"""Composition root cho Data Model Analysis service."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.data_model_analysis import DataModelAnalysisService, IDataModelAnalysisService
from src.infrastructure.agents.data_model_analysis_agent import DataModelAnalysisAgent
from src.infrastructure.analysis import PyDbmlStructureExtractor
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_analytical_requirement_repository import (
    PostgresAnalyticalRequirementRepository,
)
from src.infrastructure.repositories.postgres_data_source_repository import PostgresDataSourceRepository
from src.infrastructure.repositories.postgres_requirement_repository import PostgresRequirementRepository
from src.infrastructure.security.pii_guard import PiiGuard
from src.presentation.dependencies.data_model_resources import get_pii_guard
from src.presentation.dependencies.data_models import DataModelServiceDependency
from src.presentation.dependencies.llm import get_llm_gateway
from src.presentation.dependencies.project_access import ProjectAccessDependency


def get_data_model_analysis_service(
    access: ProjectAccessDependency,
    models: DataModelServiceDependency,
    pii_guard: Annotated[PiiGuard, Depends(get_pii_guard)],
    session: AsyncSession = Depends(get_async_db_session),
) -> IDataModelAnalysisService:
    return DataModelAnalysisService(
        access,
        models,
        PostgresRequirementRepository(session),
        PostgresAnalyticalRequirementRepository(session),
        PostgresDataSourceRepository(session),
        PyDbmlStructureExtractor(),
        DataModelAnalysisAgent(get_llm_gateway, pii_guard),
    )


DataModelAnalysisDependency = Annotated[
    IDataModelAnalysisService, Depends(get_data_model_analysis_service)
]
