"""REST endpoints cho nguồn dữ liệu của dự án."""

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, File, Response, UploadFile
from src.application.data_sources.data_source_upload_policy import MAX_FILE_SIZE
from src.application.data_sources.input import (
    DataSourceIdInput,
    ListDataSourcesInput,
    UploadDataSourcesInput,
    UploadFileInput,
)
from src.presentation.dependencies.data_sources import (
    DataSourceColumnContextDependency,
    DataSourceServiceDependency,
)
from src.presentation.dtos.data_sources.request import (
    ProjectIdPath,
    SourceIdPath,
    UpdateDataSourceColumnRequest,
)
from src.presentation.dtos.data_sources.response import (
    DataSourceListResponse,
    DataSourcePreviewResponse,
    DataSourceResponse,
    UploadDataSourcesResponse,
)
from src.presentation.routing import ApiResponseRoute, error_responses

router = APIRouter(
    prefix="/projects/{project_id}/data-sources",
    tags=["Data Sources"],
    route_class=ApiResponseRoute,
)


@router.get(
    "",
    response_model=DataSourceListResponse,
    operation_id="listProjectDataSources",
    responses=error_responses(401, 403, 404, 422, 500),
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
    responses=error_responses(401, 403, 404, 422, 500),
)
async def upload_data_sources(
    project_id: ProjectIdPath,
    service: DataSourceServiceDependency,
    files: Annotated[list[UploadFile], File(description="Tối đa 20 file CSV")],
) -> UploadDataSourcesResponse:
    """Upload và phân tích batch file CSV nếu người dùng là OWNER."""
    inputs: list[UploadFileInput] = []
    for file in files:
        inputs.append(
            UploadFileInput(
                filename=file.filename or "unknown",
                content=await file.read(MAX_FILE_SIZE + 1),
            )
        )
    output = await service.upload_data_sources(UploadDataSourcesInput(project_id, tuple(inputs)))
    return UploadDataSourcesResponse.from_application(output)


@router.get(
    "/{source_id}/preview",
    response_model=DataSourcePreviewResponse,
    operation_id="getProjectDataSourcePreview",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def get_data_source_preview(
    project_id: ProjectIdPath,
    source_id: SourceIdPath,
    service: DataSourceServiceDependency,
) -> DataSourcePreviewResponse:
    """Đọc preview CSV theo yêu cầu, không lưu bản sao trong database."""
    output = await service.get_preview(DataSourceIdInput(project_id, source_id))
    return DataSourcePreviewResponse.from_application(output)


@router.patch(
    "/{source_id}/tables/{table_name}/columns/{column_name}",
    response_model=DataSourceResponse,
    operation_id="updateProjectDataSourceColumn",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def update_data_source_column(
    request: UpdateDataSourceColumnRequest,
    context: DataSourceColumnContextDependency,
) -> DataSourceResponse:
    """Cập nhật một phần metadata của cột nếu người dùng là OWNER."""
    target, service = context
    output = await service.update_column(request.to_application(target))
    return DataSourceResponse.from_application(output)


@router.delete(
    "/{source_id}",
    status_code=HTTPStatus.NO_CONTENT,
    response_model=None,
    operation_id="deleteProjectDataSource",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def delete_data_source(
    project_id: ProjectIdPath,
    source_id: SourceIdPath,
    service: DataSourceServiceDependency,
) -> Response:
    """Xóa nguồn và file vật lý nếu người dùng là OWNER."""
    await service.delete_data_source(DataSourceIdInput(project_id, source_id))
    return Response(status_code=HTTPStatus.NO_CONTENT)

