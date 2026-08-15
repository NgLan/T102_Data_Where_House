"""Use Case: Xem chi tiết đề xuất thay đổi mô hình dữ liệu (UC6.1)."""

from src.application.data_models.dto import (
    ChangeProposalDetailOutput,
    GetChangeProposalInput,
)
from src.application.data_models.i_get_change_proposal_service import (
    IGetChangeProposalService,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.repository import (
    IDataModelChangeRepository,
    IDataModelRepository,
)


class GetChangeProposalService(IGetChangeProposalService):
    """Triển khai use case xem chi tiết đề xuất thay đổi kèm mô hình hiện hành.

    Trả về đồng thời `proposed_dbml` và `current_dbml` để Frontend dựng được khung so sánh
    khác biệt (Diff View) chỉ với một lần gọi API.
    """

    def __init__(
        self,
        data_model_repository: IDataModelRepository,
        change_repository: IDataModelChangeRepository,
    ) -> None:
        """Khởi tạo use case với repository mô hình dữ liệu và repository đề xuất."""
        self._data_model_repository: IDataModelRepository = data_model_repository
        self._change_repository: IDataModelChangeRepository = change_repository

    async def execute(self, payload: GetChangeProposalInput) -> ChangeProposalDetailOutput:
        """Trả về nội dung đề xuất kèm DBML hiện hành để đối chiếu khác biệt."""
        change: DataModelChange | None = await self._change_repository.get_by_id(
            payload.change_id
        )
        if change is None:
            raise BusinessException(
                code=ErrorCode.PROPOSAL_NOT_FOUND,
                message=f"Không tìm thấy đề xuất thay đổi '{payload.change_id}'.",
            )

        data_model: DataModel | None = await self._data_model_repository.get_by_id(
            change.data_model_id
        )
        if data_model is None:
            raise BusinessException(
                code=ErrorCode.DATA_MODEL_NOT_FOUND,
                message=(
                    f"Đề xuất '{change.id}' tham chiếu tới mô hình dữ liệu "
                    f"'{change.data_model_id}' không còn tồn tại."
                ),
            )

        return self._to_detail(change, data_model)

    def _to_detail(
        self, change: DataModelChange, data_model: DataModel
    ) -> ChangeProposalDetailOutput:
        """Ghép thực thể đề xuất và mô hình hiện hành thành DTO chi tiết."""
        return ChangeProposalDetailOutput(
            id=change.id,
            data_model_id=change.data_model_id,
            user_id=change.user_id,
            base_revision=change.base_revision,
            proposed_dbml=change.proposed_dbml,
            status=change.status,
            current_dbml=data_model.dbml,
            current_revision=data_model.revision,
            is_outdated=change.base_revision != data_model.revision,
            created_at=change.created_at,
            updated_at=change.updated_at,
        )
