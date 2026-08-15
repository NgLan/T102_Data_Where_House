"""API Endpoints v1 cho Đề xuất Thay đổi Mô hình Dữ liệu (Proposals) — UC6.1."""

from uuid import UUID

from fastapi import APIRouter
from src.application.data_models.dto import GetChangeProposalInput
from src.common.dto.response import ApiResponse
from src.presentation.dependencies.application import GetChangeProposalUseCase
from src.presentation.schemas.data_model_changes.response import (
    ChangeProposalDetailResponse,
)

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
