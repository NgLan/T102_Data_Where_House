"""Use Case: Tạo đề xuất thay đổi mô hình dữ liệu bằng AI (T-024 / FR5.2).

Tương ứng Bước 5 của `docs/guide_cho_ca_nhom/data_flow.md`: người dùng gửi prompt chỉnh sửa,
Agent sinh DBML mới và hệ thống ghi lại thành một bản ghi `data_model_changes` ở trạng thái
`PROPOSED` với `base_revision` bằng revision hiện tại của mô hình.
"""

from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.dto import (
    ChangeProposalDetailOutput,
    ReviseDataModelInput,
)
from src.application.data_models.i_create_change_proposal_service import (
    ICreateChangeProposalService,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.logging import get_logger
from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.repository import (
    IDataModelChangeRepository,
    IDataModelRepository,
)
from src.domain.data_model.revision import DbmlRevisionProposal, IDataModelReviser
from src.domain.project.repository import IProjectRepository
from src.domain.shared.types import EntityID

logger = get_logger(__name__)


class CreateChangeProposalService(ICreateChangeProposalService):
    """Triển khai use case nhờ AI chỉnh sửa mô hình dữ liệu và lưu đề xuất."""

    def __init__(
        self,
        data_model_repository: IDataModelRepository,
        change_repository: IDataModelChangeRepository,
        reviser: IDataModelReviser,
        project_repository: IProjectRepository,
        unit_of_work: IUnitOfWork,
    ) -> None:
        """Khởi tạo use case với các repository, bộ chỉnh sửa AI và đơn vị công việc."""
        self._data_model_repository: IDataModelRepository = data_model_repository
        self._change_repository: IDataModelChangeRepository = change_repository
        self._reviser: IDataModelReviser = reviser
        self._project_repository: IProjectRepository = project_repository
        self._unit_of_work: IUnitOfWork = unit_of_work

    async def execute(self, payload: ReviseDataModelInput) -> ChangeProposalDetailOutput:
        """Sinh đề xuất DBML mới bằng AI và lưu lại ở trạng thái PROPOSED."""
        data_model = await self._load_data_model(payload.data_model_id)
        author_id = await self._resolve_author(data_model)

        proposal: DbmlRevisionProposal = await self._reviser.revise(
            data_model.dbml, payload.instruction
        )

        change = DataModelChange(
            data_model_id=data_model.id,
            user_id=author_id,
            base_revision=data_model.revision,
            proposed_dbml=proposal.dbml,
        )
        await self._change_repository.save(change)
        await self._unit_of_work.commit()

        logger.info(
            "change_proposal_created change_id=%s data_model_id=%s base_revision=%d attempts=%d",
            change.id,
            data_model.id,
            change.base_revision,
            proposal.attempts,
        )
        return self._to_detail(change, data_model, proposal.summary)

    async def _load_data_model(self, data_model_id: EntityID) -> DataModel:
        """Nạp mô hình dữ liệu theo ID, ném lỗi nghiệp vụ nếu không tồn tại."""
        data_model = await self._data_model_repository.get_by_id(data_model_id)
        if data_model is None:
            raise BusinessException(
                code=ErrorCode.DATA_MODEL_NOT_FOUND,
                message=f"Không tìm thấy mô hình dữ liệu '{data_model_id}'.",
            )
        return data_model

    async def _resolve_author(self, data_model: DataModel) -> EntityID:
        """Xác định người đứng tên đề xuất.

        Hệ thống chưa có xác thực nên tạm quy về chủ sở hữu dự án. Khi bổ sung Auth, chỗ này
        sẽ thay bằng người dùng đang đăng nhập.
        """
        project = await self._project_repository.get_by_id(data_model.project_id)
        if project is None:
            raise BusinessException(
                code=ErrorCode.PROJECT_NOT_FOUND,
                message=(
                    f"Mô hình dữ liệu '{data_model.id}' tham chiếu tới dự án "
                    f"'{data_model.project_id}' không còn tồn tại."
                ),
            )
        return project.user_id

    def _to_detail(
        self, change: DataModelChange, data_model: DataModel, summary: str
    ) -> ChangeProposalDetailOutput:
        """Ghép đề xuất vừa tạo với mô hình hiện hành thành DTO chi tiết."""
        return ChangeProposalDetailOutput(
            id=change.id,
            data_model_id=change.data_model_id,
            user_id=change.user_id,
            base_revision=change.base_revision,
            proposed_dbml=change.proposed_dbml,
            status=change.status,
            current_dbml=data_model.dbml,
            current_revision=data_model.revision,
            is_outdated=False,
            summary=summary,
            created_at=change.created_at,
            updated_at=change.updated_at,
        )
