"""Use Case: Chấp nhận đề xuất thay đổi mô hình dữ liệu (UC6.2 / T-032)."""

from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.dto import AcceptChangeProposalInput, DataModelOutput
from src.application.data_models.i_accept_change_proposal_service import (
    IAcceptChangeProposalService,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.logging import get_logger
from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.repository import (
    IDataModelChangeRepository,
    IDataModelRepository,
)
from src.domain.shared.types import EntityID

logger = get_logger(__name__)


class AcceptChangeProposalService(IAcceptChangeProposalService):
    """Triển khai use case chấp nhận đề xuất và áp dụng vào mô hình dữ liệu chính thức.

    Toàn bộ quy tắc nghiệp vụ (kiểm tra trạng thái, khóa lạc quan theo revision, tăng
    revision) nằm ở `DataModel.apply_change()`. Use case chỉ điều phối nạp dữ liệu,
    lưu trữ và chốt giao dịch.
    """

    def __init__(
        self,
        data_model_repository: IDataModelRepository,
        change_repository: IDataModelChangeRepository,
        unit_of_work: IUnitOfWork,
    ) -> None:
        """Khởi tạo use case với hai repository và đơn vị công việc giao dịch."""
        self._data_model_repository: IDataModelRepository = data_model_repository
        self._change_repository: IDataModelChangeRepository = change_repository
        self._unit_of_work: IUnitOfWork = unit_of_work

    async def execute(self, payload: AcceptChangeProposalInput) -> DataModelOutput:
        """Áp dụng đề xuất vào mô hình dữ liệu và trả về mô hình sau khi cập nhật."""
        change = await self._load_change(payload.change_id)
        data_model = await self._load_data_model(change)

        await self._apply(data_model, change)

        await self._data_model_repository.save(data_model)
        await self._change_repository.save(change)
        await self._unit_of_work.commit()

        logger.info(
            "change_proposal_accepted change_id=%s data_model_id=%s revision=%d",
            change.id,
            data_model.id,
            data_model.revision,
        )
        return DataModelOutput(
            id=data_model.id,
            project_id=data_model.project_id,
            dbml=data_model.dbml,
            revision=data_model.revision,
            created_at=data_model.created_at,
            updated_at=data_model.updated_at,
        )

    async def _apply(self, data_model: DataModel, change: DataModelChange) -> None:
        """Áp dụng đề xuất, đồng thời lưu lại trạng thái CONFLICTED khi xung đột revision.

        Khi `base_revision` không còn khớp, tầng Domain đánh dấu đề xuất là CONFLICTED rồi
        mới ném ngoại lệ. Trạng thái đó phải được chốt xuống CSDL bằng một giao dịch riêng,
        nếu không việc đánh dấu sẽ mất trắng khi ngoại lệ lan lên trên.

        Chỉ mã lỗi REVISION_CONFLICT mới ứng với việc Domain vừa đánh dấu trong lần gọi này.
        Không được dựa vào `change.status == CONFLICTED` vì đề xuất có thể đã mang sẵn trạng
        thái đó từ trước — khi ấy ngoại lệ là INVALID_PROPOSAL_STATUS_TRANSITION và tuyệt đối
        không được ghi gì xuống CSDL.
        """
        try:
            data_model.apply_change(change)
        except BusinessException as exc:
            if exc.code == ErrorCode.REVISION_CONFLICT:
                await self._change_repository.save(change)
                await self._unit_of_work.commit()
                logger.warning(
                    "change_proposal_conflicted change_id=%s base_revision=%d current_revision=%d",
                    change.id,
                    change.base_revision,
                    data_model.revision,
                )
            raise

    async def _load_change(self, change_id: EntityID) -> DataModelChange:
        """Nạp đề xuất thay đổi theo ID, ném lỗi nghiệp vụ nếu không tồn tại."""
        change = await self._change_repository.get_by_id(change_id)
        if change is None:
            raise BusinessException(
                code=ErrorCode.PROPOSAL_NOT_FOUND,
                message=f"Không tìm thấy đề xuất thay đổi '{change_id}'.",
            )
        return change

    async def _load_data_model(self, change: DataModelChange) -> DataModel:
        """Nạp mô hình dữ liệu gốc của đề xuất, ném lỗi nghiệp vụ nếu không tồn tại."""
        data_model = await self._data_model_repository.get_by_id(change.data_model_id)
        if data_model is None:
            raise BusinessException(
                code=ErrorCode.DATA_MODEL_NOT_FOUND,
                message=(
                    f"Đề xuất '{change.id}' tham chiếu tới mô hình dữ liệu "
                    f"'{change.data_model_id}' không còn tồn tại."
                ),
            )
        return data_model
