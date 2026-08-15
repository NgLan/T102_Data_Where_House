"""Use Case: Liệt kê đề xuất thay đổi của một mô hình dữ liệu (UC6.1)."""

from src.application.data_models.dto import (
    ChangeProposalSummaryOutput,
    ListChangeProposalsInput,
)
from src.application.data_models.i_list_change_proposals_service import (
    IListChangeProposalsService,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModelChange
from src.domain.data_model.repository import (
    IDataModelChangeRepository,
    IDataModelRepository,
)


class ListChangeProposalsService(IListChangeProposalsService):
    """Triển khai use case liệt kê đề xuất thay đổi của một mô hình dữ liệu."""

    def __init__(
        self,
        data_model_repository: IDataModelRepository,
        change_repository: IDataModelChangeRepository,
    ) -> None:
        """Khởi tạo use case với repository mô hình dữ liệu và repository đề xuất."""
        self._data_model_repository: IDataModelRepository = data_model_repository
        self._change_repository: IDataModelChangeRepository = change_repository

    async def execute(
        self, payload: ListChangeProposalsInput
    ) -> list[ChangeProposalSummaryOutput]:
        """Trả về danh sách đề xuất thay đổi, mới nhất trước."""
        if await self._data_model_repository.get_by_id(payload.data_model_id) is None:
            raise BusinessException(
                code=ErrorCode.DATA_MODEL_NOT_FOUND,
                message=f"Không tìm thấy mô hình dữ liệu '{payload.data_model_id}'.",
            )

        changes: list[DataModelChange] = await self._change_repository.list_by_data_model(
            payload.data_model_id
        )
        if payload.status is not None:
            changes = [change for change in changes if change.status == payload.status]
        return [self._to_summary(change) for change in changes]

    def _to_summary(self, change: DataModelChange) -> ChangeProposalSummaryOutput:
        """Chuyển thực thể đề xuất thay đổi thành DTO tóm tắt."""
        return ChangeProposalSummaryOutput(
            id=change.id,
            data_model_id=change.data_model_id,
            user_id=change.user_id,
            base_revision=change.base_revision,
            status=change.status,
            created_at=change.created_at,
            updated_at=change.updated_at,
        )
