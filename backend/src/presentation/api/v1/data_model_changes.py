"""REST endpoints cho đề xuất thay đổi Data Model."""

from fastapi import APIRouter
from src.application.data_models.input import (
    ChangeProposalIdInput,
    GetChangeProposalInput,
    GetPendingChangeProposalInput,
)
from src.presentation.dependencies.data_models import DataModelServiceDependency
from src.presentation.dtos.data_model_changes.request import ChangeIdPath
from src.presentation.dtos.data_model_changes.response import (
    ChangeProposalDetailResponse,
    ChangeProposalSummaryResponse,
)
from src.presentation.dtos.data_models.request import ProjectIdPath
from src.presentation.dtos.data_models.response import DataModelResponse
from src.presentation.routing import ApiResponseRoute, error_responses

router = APIRouter(
    prefix="",
    tags=["Data Model Changes"],
    route_class=ApiResponseRoute,
)


@router.get(
    "/projects/{project_id}/data-model-changes/pending",
    response_model=ChangeProposalDetailResponse | None,
    operation_id="getPendingProjectDataModelChange",
    responses=error_responses(401, 403, 404, 500),
)
async def get_pending_change_proposal(
    project_id: ProjectIdPath,
    service: DataModelServiceDependency,
) -> ChangeProposalDetailResponse | None:
    result = await service.get_pending_change_proposal(
        GetPendingChangeProposalInput(project_id)
    )
    return ChangeProposalDetailResponse.from_application(result) if result else None


@router.get(
    "/projects/{project_id}/data-model-changes/{change_id}",
    response_model=ChangeProposalDetailResponse,
    operation_id="getProjectDataModelChange",
    summary="Xem chi tiết một đề xuất thay đổi mô hình dữ liệu",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def get_change_proposal(
    project_id: ProjectIdPath,
    change_id: ChangeIdPath,
    service: DataModelServiceDependency,
) -> ChangeProposalDetailResponse:
    """Trả về DBML đề xuất kèm DBML hiện hành để dựng khung so sánh khác biệt."""
    result = await service.get_change_proposal(GetChangeProposalInput(project_id=project_id, change_id=change_id))
    return ChangeProposalDetailResponse.from_application(result)


@router.post(
    "/data-model-changes/{change_id}/accept",
    response_model=DataModelResponse,
    operation_id="acceptChangeProposal",
    summary="Chấp nhận đề xuất và áp dụng vào mô hình dữ liệu hiện tại",
    responses=error_responses(401, 403, 404, 409, 422, 500),
)
async def accept_change_proposal(
    change_id: ChangeIdPath,
    service: DataModelServiceDependency,
) -> DataModelResponse:
    """Áp dụng DBML đề xuất vào mô hình dữ liệu, tăng revision và trả về mô hình mới."""
    result = await service.accept_change_proposal(ChangeProposalIdInput(change_id=change_id))
    return DataModelResponse.from_application(result)


@router.post(
    "/data-model-changes/{change_id}/reject",
    response_model=ChangeProposalSummaryResponse,
    operation_id="rejectChangeProposal",
    summary="Từ chối một đề xuất thay đổi mô hình dữ liệu",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def reject_change_proposal(
    change_id: ChangeIdPath,
    service: DataModelServiceDependency,
) -> ChangeProposalSummaryResponse:
    """Đánh dấu đề xuất là REJECTED; nội dung và revision của mô hình giữ nguyên."""
    result = await service.reject_change_proposal(ChangeProposalIdInput(change_id=change_id))
    return ChangeProposalSummaryResponse.model_validate(result)
