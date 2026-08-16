"""REST endpoints cho nguồn dữ liệu của dự án."""

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, File, Response, UploadFile
from src.application.data_sources.data_source_rules import MAX_FILE_SIZE
from src.application.data_sources.input import (
    DataSourceIdInput,
    ListDataSourcesInput,
    UploadDataSourcesInput,
    UploadFileInput,
)
from src.presentation.dependencies.data_sources import DataSourceServiceDependency
from src.presentation.dtos.common import ApiErrorResponse
from src.presentation.dtos.data_sources.request import (
    DataSourceIdPath,
    ProjectIdPath,
    UpdateDataSourceColumnRequest,
)
from src.presentation.dtos.data_sources.response import (
    DataSourceListResponse,
    DataSourcePreviewResponse,
    DataSourceResponse,
    UploadDataSourcesResponse,
)
from src.presentation.routing import ApiResponseRoute, ErrorResponses


router = APIRouter(
    prefix="/projects/{project_id}/data-sources",
    tags=["Data Sources"],
    route_class=ApiResponseRoute,
)
ERROR_RESPONSES: ErrorResponses = {
    401: {"model": ApiErrorResponse},
    403: {"model": ApiErrorResponse},
    404: {"model": ApiErrorResponse},
    422: {"model": ApiErrorResponse},
    500: {"model": ApiErrorResponse},
}


@router.get(
    "",
    response_model=DataSourceListResponse,
    operation_id="listProjectDataSources",
    responses=ERROR_RESPONSES,
)
async def list_data_sources(
    project_id: ProjectIdPath,
    service: DataSourceServiceDependency,
) -> DataSourceListResponse:
    """Liệt kê nguồn nếu người dùng là thành viên dự án."""
    output = await service.list_data_sources(ListDataSourcesInput(project_id))
    return DataSourceListResponse.from_application(output)


@router.post(
    "/upload",
    response_model=UploadDataSourcesResponse,
    status_code=HTTPStatus.CREATED,
    operation_id="uploadProjectDataSources",
    responses=ERROR_RESPONSES,
)
async def upload_data_sources(
    project_id: ProjectIdPath,
    service: DataSourceServiceDependency,
    files: Annotated[list[UploadFile], File(description="Tối đa 20 file CSV hoặc DOCX")],
) -> UploadDataSourcesResponse:
    """Upload và phân tích batch file nếu người dùng là OWNER."""
    inputs: list[UploadFileInput] = []
    for file in files:
        inputs.append(
            UploadFileInput(
                filename=file.filename or "unknown",
                content=await file.read(MAX_FILE_SIZE + 1),
            )
        )
    output = await service.upload_data_sources(
        UploadDataSourcesInput(project_id, tuple(inputs))
    )
    return UploadDataSourcesResponse.from_application(output)


@router.get(
    "/{data_source_id}/preview",
    response_model=DataSourcePreviewResponse,
    operation_id="getProjectDataSourcePreview",
    responses=ERROR_RESPONSES,
)
async def get_data_source_preview(
    project_id: ProjectIdPath,
    data_source_id: DataSourceIdPath,
    service: DataSourceServiceDependency,
) -> DataSourcePreviewResponse:
    """Đọc preview CSV theo yêu cầu, không lưu bản sao trong database."""
    output = await service.get_preview(DataSourceIdInput(project_id, data_source_id))
    return DataSourcePreviewResponse.from_application(output)


@router.patch(
    "/{data_source_id}/column",
    response_model=DataSourceResponse,
    operation_id="updateProjectDataSourceColumn",
    responses=ERROR_RESPONSES,
)
async def update_data_source_column(
    project_id: ProjectIdPath,
    data_source_id: DataSourceIdPath,
    request: UpdateDataSourceColumnRequest,
    service: DataSourceServiceDependency,
) -> DataSourceResponse:
    """Cập nhật kiểu và options của một cột nếu người dùng là OWNER."""
    output = await service.update_column(request.to_application(project_id, data_source_id))
    return DataSourceResponse.from_application(output)


@router.delete(
    "/{data_source_id}",
    status_code=HTTPStatus.NO_CONTENT,
    response_model=None,
    operation_id="deleteProjectDataSource",
    responses=ERROR_RESPONSES,
)
async def delete_data_source(
    project_id: ProjectIdPath,
    data_source_id: DataSourceIdPath,
    service: DataSourceServiceDependency,
) -> Response:
    """Xóa nguồn và file vật lý nếu người dùng là OWNER."""
    await service.delete_data_source(DataSourceIdInput(project_id, data_source_id))
    return Response(status_code=HTTPStatus.NO_CONTENT)
