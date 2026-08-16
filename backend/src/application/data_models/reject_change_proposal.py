"""Use Case: Từ chối đề xuất thay đổi mô hình dữ liệu (UC6.3 / T-033)."""

from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.dto import (
    ChangeProposalSummaryOutput,
    RejectChangeProposalInput,
)
from src.application.data_models.i_reject_change_proposal_service import (
    IRejectChangeProposalService,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.logging import get_logger
from src.domain.data_model.entities import DataModelChange
from src.domain.data_model.repository import IDataModelChangeRepository

logger = get_logger(__name__)


class RejectChangeProposalService(IRejectChangeProposalService):
    """Triển khai use case từ chối đề xuất thay đổi.

    Từ chối chỉ đổi trạng thái của đề xuất; nội dung DBML và revision của mô hình dữ liệu
    giữ nguyên hoàn toàn (Edge case 6 trong docs/guide_cho_ca_nhom/database.md).
    """

    def __init__(
        self,
        change_repository: IDataModelChangeRepository,
        unit_of_work: IUnitOfWork,
    ) -> None:
        """Khởi tạo use case với repository đề xuất và đơn vị công việc giao dịch."""
        self._change_repository: IDataModelChangeRepository = change_repository
        self._unit_of_work: IUnitOfWork = unit_of_work

    async def execute(
        self, payload: RejectChangeProposalInput
    ) -> ChangeProposalSummaryOutput:
        """Đánh dấu đề xuất là REJECTED và trả về thông tin tóm tắt sau khi cập nhật."""
        change: DataModelChange | None = await self._change_repository.get_by_id(
            payload.change_id
        )
        if change is None:
            raise BusinessException(
                code=ErrorCode.PROPOSAL_NOT_FOUND,
                message=f"Không tìm thấy đề xuất thay đổi '{payload.change_id}'.",
            )

        change.mark_rejected()

        await self._change_repository.save(change)
        await self._unit_of_work.commit()

        logger.info("change_proposal_rejected change_id=%s", change.id)
        return ChangeProposalSummaryOutput(
            id=change.id,
            data_model_id=change.data_model_id,
            user_id=change.user_id,
            base_revision=change.base_revision,
            status=change.status,
            created_at=change.created_at,
            updated_at=change.updated_at,
        )
