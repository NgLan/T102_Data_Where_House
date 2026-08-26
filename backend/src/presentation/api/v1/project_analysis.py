"""REST endpoints cho Analyze Changes và trạng thái outdated."""

from uuid import UUID

from fastapi import APIRouter
from src.application.data_warehouse_workflows.input import (
    GetAnalysisStatusInput,
    GetSourceCoverageInput,
    ReanalyzeProjectInput,
)
from src.application.project_initialization import ProjectInitializationInput
from src.presentation.dependencies.data_warehouse_workflows import DataWarehouseWorkflowDependency
from src.presentation.dependencies.project_initialization import (
    ProjectInitializationServiceDependency,
)
from src.presentation.dtos.data_models.request import ProjectIdPath
from src.presentation.dtos.data_warehouse_workflows.response import AnalysisStatusResponse
from src.presentation.dtos.project_initialization import ProjectInitializationResponse
from src.presentation.dtos.source_coverage import (
    RecheckSourceCoverageRequest,
    ResolveSourceCoverageRequest,
)
from src.presentation.routing import ApiResponseRoute, error_responses

router = APIRouter(
    prefix="/projects/{project_id}",
    tags=["Project Analysis"],
    route_class=ApiResponseRoute,
)


@router.get(
    "/analysis-status",
    response_model=AnalysisStatusResponse,
    operation_id="getProjectAnalysisStatus",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def get_project_analysis_status(
    project_id: ProjectIdPath,
    service: DataWarehouseWorkflowDependency,
) -> AnalysisStatusResponse:
    """Đọc trạng thái outdated mà không gọi LLM."""
    output = await service.get_analysis_status(GetAnalysisStatusInput(project_id))
    return AnalysisStatusResponse.from_application(output)


@router.post(
    "/reanalyze",
    response_model=AnalysisStatusResponse,
    operation_id="reanalyzeProject",
    responses=error_responses(401, 403, 404, 409, 422, 500, 502),
)
async def reanalyze_project(
    project_id: ProjectIdPath,
    service: DataWarehouseWorkflowDependency,
) -> AnalysisStatusResponse:
    """Chạy RequirementAgent cho những analysis đã outdated."""
    output = await service.reanalyze(ReanalyzeProjectInput(project_id))
    return AnalysisStatusResponse.from_application(output)


@router.get(
    "/source-coverage",
    response_model=AnalysisStatusResponse,
    operation_id="getProjectSourceCoverage",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def get_source_coverage(
    project_id: ProjectIdPath,
    service: DataWarehouseWorkflowDependency,
) -> AnalysisStatusResponse:
    """Reload persisted Source Coverage and readiness state."""
    output = await service.get_source_coverage(GetSourceCoverageInput(project_id))
    return AnalysisStatusResponse.from_application(output)


@router.post(
    "/source-coverage/{assessment_id}/resolution",
    response_model=AnalysisStatusResponse,
    operation_id="resolveProjectSourceCoverage",
    responses=error_responses(400, 401, 403, 404, 409, 422, 500, 502),
)
async def resolve_source_coverage(
    project_id: ProjectIdPath,
    assessment_id: UUID,
    payload: ResolveSourceCoverageRequest,
    service: DataWarehouseWorkflowDependency,
) -> AnalysisStatusResponse:
    """Persist one owner-only Source Confirmation item without invoking an Agent."""
    output = await service.resolve_source_coverage(
        payload.to_application(project_id, assessment_id)
    )
    return AnalysisStatusResponse.from_application(output)


@router.post(
    "/source-coverage/recheck",
    response_model=AnalysisStatusResponse,
    operation_id="recheckProjectSourceCoverage",
    responses=error_responses(400, 401, 403, 404, 409, 422, 500, 502),
)
async def recheck_source_coverage(
    project_id: ProjectIdPath,
    payload: RecheckSourceCoverageRequest,
    service: DataWarehouseWorkflowDependency,
) -> AnalysisStatusResponse:
    """Materialize a completed batch and invoke only Source Coverage once."""
    output = await service.recheck_source_coverage(payload.to_application(project_id))
    return AnalysisStatusResponse.from_application(output)


@router.post(
    "/initialize",
    response_model=ProjectInitializationResponse,
    operation_id="runProjectInitializationWorkflow",
    responses=error_responses(401, 403, 404, 409, 422, 500, 502),
)
async def initialize_project(
    project_id: ProjectIdPath,
    service: ProjectInitializationServiceDependency,
) -> ProjectInitializationResponse:
    """Chạy Requirement → Source analysis → DBML và pause khi cần clarification."""
    output = await service.run(ProjectInitializationInput(project_id))
    return ProjectInitializationResponse.from_application(output)

