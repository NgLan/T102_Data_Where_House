"""API Endpoints v1 cho Đề xuất Thay đổi Mô hình Dữ liệu (Proposals) — UC6.1."""

from uuid import UUID

from fastapi import APIRouter
from src.application.data_models.dto import (
    AcceptChangeProposalInput,
    GetChangeProposalInput,
    RejectChangeProposalInput,
)
from src.common.dto.response import ApiResponse
from src.presentation.dependencies.application import (
    AcceptChangeProposalUseCase,
    GetChangeProposalUseCase,
    RejectChangeProposalUseCase,
)
from src.presentation.schemas.data_model_changes.response import (
    ChangeProposalDetailResponse,
    ChangeProposalSummaryResponse,
)
from src.presentation.schemas.data_models.response import DataModelResponse

router = APIRouter(prefix="/data-model-changes", tags=["Data Model Changes"])


@router.get(
    "/{change_id}",
    response_model=ApiResponse[ChangeProposalDetailResponse],
    summary="Xem chi tiết một đề xuất thay đổi mô hình dữ liệu",
)
async def get_change_proposal(
    change_id: UUID,
    use_case: GetChangeProposalUseCase,
) -> ApiResponse[ChangeProposalDetailResponse]:
    """Trả về DBML đề xuất kèm DBML hiện hành và base revision để dựng khung so sánh."""
    result = await use_case.execute(GetChangeProposalInput(change_id=change_id))
    return ApiResponse[ChangeProposalDetailResponse](
        message="Lấy chi tiết đề xuất thay đổi thành công.",
        data=ChangeProposalDetailResponse.model_validate(result.model_dump()),
    )


@router.post(
    "/{change_id}/accept",
    response_model=ApiResponse[DataModelResponse],
    summary="Chấp nhận đề xuất và áp dụng vào mô hình dữ liệu hiện tại",
)
async def accept_change_proposal(
    change_id: UUID,
    use_case: AcceptChangeProposalUseCase,
) -> ApiResponse[DataModelResponse]:
    """Áp dụng DBML đề xuất vào mô hình dữ liệu, tăng revision và trả về mô hình mới."""
    result = await use_case.execute(AcceptChangeProposalInput(change_id=change_id))
    return ApiResponse[DataModelResponse](
        message="Áp dụng đề xuất thay đổi thành công.",
        data=DataModelResponse.model_validate(result.model_dump()),
    )


@router.post(
    "/{change_id}/reject",
    response_model=ApiResponse[ChangeProposalSummaryResponse],
    summary="Từ chối một đề xuất thay đổi mô hình dữ liệu",
)
async def reject_change_proposal(
    change_id: UUID,
    use_case: RejectChangeProposalUseCase,
) -> ApiResponse[ChangeProposalSummaryResponse]:
    """Đánh dấu đề xuất là REJECTED; nội dung và revision của mô hình dữ liệu giữ nguyên."""
    result = await use_case.execute(RejectChangeProposalInput(change_id=change_id))
    return ApiResponse[ChangeProposalSummaryResponse](
        message="Từ chối đề xuất thay đổi thành công.",
        data=ChangeProposalSummaryResponse.model_validate(result.model_dump()),
    )
