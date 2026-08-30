"""REST endpoints cho Data Model hiện tại của dự án."""

from fastapi import APIRouter, Query
from src.application.data_model_analysis.models import GenerateAnalysisDocumentInput
from src.application.data_models.input import GenerateDataModelDdlInput, GetDataModelInput
from src.domain.sandbox.enums import SandboxDbType
from src.presentation.dependencies.data_model_analysis import DataModelAnalysisDependency
from src.presentation.dependencies.data_models import DataModelServiceDependency
from src.presentation.dtos.data_models.request import (
    GenerateAnalysisDocumentRequest,
    ProjectIdPath,
    UpdateDataModelRequest,
    ValidateDataModelRequest,
)
from src.presentation.dtos.data_models.response import (
    AnalysisDocumentResponse,
    DataModelDdlResponse,
    DataModelResponse,
    DataModelValidationIssueResponse,
)
from src.presentation.routing import ApiResponseRoute, error_responses

router = APIRouter(
    prefix="/projects/{project_id}/data-model",
    tags=["Data Models"],
    route_class=ApiResponseRoute,
)


@router.get(
    "",
    response_model=DataModelResponse,
    operation_id="getDataModel",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def get_current_data_model(
    project_id: ProjectIdPath,
    service: DataModelServiceDependency,
) -> DataModelResponse:
    """Lấy DBML và revision hiện tại của dự án."""
    output = await service.get_data_model(GetDataModelInput(project_id=project_id))
    return DataModelResponse.from_application(output)


@router.put(
    "",
    response_model=DataModelResponse,
    operation_id="updateDataModel",
    responses=error_responses(401, 403, 404, 409, 422, 500),
)
async def update_current_data_model(
    project_id: ProjectIdPath,
    request: UpdateDataModelRequest,
    service: DataModelServiceDependency,
) -> DataModelResponse:
    """Lưu trực tiếp DBML do người dùng chỉnh sửa thủ công."""
    output = await service.update_data_model(request.to_application(project_id))
    return DataModelResponse.from_application(output)


@router.get(
    "/validation-issues",
    response_model=list[DataModelValidationIssueResponse],
    operation_id="getDataModelValidationIssues",
    responses=error_responses(401, 403, 404, 500),
)
async def get_data_model_validation_issues(
    project_id: ProjectIdPath,
    service: DataModelServiceDependency,
) -> list[DataModelValidationIssueResponse]:
    """Trả các lỗi và cảnh báo validation của snapshot DBML hiện tại."""
    issues = await service.get_validation_issues(GetDataModelInput(project_id=project_id))
    return [DataModelValidationIssueResponse.from_application(item) for item in issues]


@router.post(
    "/validate",
    response_model=list[DataModelValidationIssueResponse],
    operation_id="validateDataModelDraft",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def validate_data_model_draft(
    project_id: ProjectIdPath,
    request: ValidateDataModelRequest,
    service: DataModelServiceDependency,
) -> list[DataModelValidationIssueResponse]:
    """Kiểm tra draft hiện tại mà không gọi LLM hoặc ghi snapshot."""
    issues = await service.validate_draft(request.to_application(project_id))
    return [DataModelValidationIssueResponse.from_application(item) for item in issues]


@router.get(
    "/ddl",
    response_model=DataModelDdlResponse,
    operation_id="generateDataModelDdl",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def generate_data_model_ddl(
    project_id: ProjectIdPath,
    service: DataModelServiceDependency,
    db_type: SandboxDbType = Query(default=SandboxDbType.POSTGRESQL),
) -> DataModelDdlResponse:
    """Sinh DDL từ revision Data Model hiện hành."""
    output = await service.generate_ddl(GenerateDataModelDdlInput(project_id, db_type))
    return DataModelDdlResponse.from_application(output)


@router.post(
    "/analysis-document",
    response_model=AnalysisDocumentResponse,
    operation_id="generateDataModelAnalysisDocument",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def generate_data_model_analysis_document(
    project_id: ProjectIdPath,
    request: GenerateAnalysisDocumentRequest,
    service: DataModelAnalysisDependency,
) -> AnalysisDocumentResponse:
    output = await service.generate_document(
        GenerateAnalysisDocumentInput(project_id, request.target(), request.locale)
    )
    return AnalysisDocumentResponse.from_application(output)
