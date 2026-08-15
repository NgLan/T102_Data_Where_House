"""REST endpoints cho Data Model hiện tại của dự án."""

from fastapi import APIRouter
from src.application.data_models.input import GetDataModelInput
from src.presentation.dependencies.data_models import DataModelServiceDependency
from src.presentation.dtos.common import ApiErrorResponse
from src.presentation.dtos.data_models.request import (
    ProjectIdPath,
    UpdateDataModelRequest,
)
from src.presentation.dtos.data_models.response import DataModelResponse
from src.presentation.routing import ApiResponseRoute

router = APIRouter(
    prefix="/projects/{project_id}/data-model",
    tags=["Data Models"],
    route_class=ApiResponseRoute,
)


@router.get(
    "",
    response_model=DataModelResponse,
    operation_id="getDataModel",
    responses={
        404: {"model": ApiErrorResponse},
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
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
    responses={
        404: {"model": ApiErrorResponse},
        409: {"model": ApiErrorResponse},
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def update_current_data_model(
    project_id: ProjectIdPath,
    request: UpdateDataModelRequest,
    service: DataModelServiceDependency,
) -> DataModelResponse:
    """Lưu snapshot DBML mới bằng optimistic locking."""
    output = await service.update_data_model(request.to_application(project_id))
    return DataModelResponse.from_application(output)
