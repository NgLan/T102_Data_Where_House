"""Kiểm thử Use Case tạo đề xuất bằng AI (T-024), chấp nhận (T-032) và từ chối (T-033).

Không gọi LLM thật: `IDataModelReviser` được thay bằng bản giả lập.
"""

from types import TracebackType
from uuid import uuid4

import pytest
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.accept_change_proposal import AcceptChangeProposalService
from src.application.data_models.create_change_proposal import CreateChangeProposalService
from src.application.data_models.dto import (
    AcceptChangeProposalInput,
    RejectChangeProposalInput,
    ReviseDataModelInput,
)
from src.application.data_models.reject_change_proposal import RejectChangeProposalService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.enums import DataModelChangeStatus
from src.domain.data_model.revision import DbmlRevisionProposal, IDataModelReviser
from src.domain.project.entities import Project
from src.domain.project.repository import IProjectRepository
from src.domain.shared.types import EntityID

from tests.test_application.test_data_model_use_cases import (
    PROPOSED_DBML,
    SAMPLE_DBML,
    FakeChangeRepository,
    FakeDataModelRepository,
)


class FakeUnitOfWork(IUnitOfWork):
    """Đơn vị công việc giả lập, đếm số lần chốt và hủy giao dịch."""

    def __init__(self) -> None:
        """Khởi tạo bộ đếm giao dịch."""
        self.commit_count: int = 0
        self.rollback_count: int = 0

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Rollback nếu khối lệnh kết thúc do ngoại lệ."""
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        """Ghi nhận một lần chốt giao dịch."""
        self.commit_count += 1

    async def rollback(self) -> None:
        """Ghi nhận một lần hủy giao dịch."""
        self.rollback_count += 1


class FakeProjectRepository(IProjectRepository):
    """Repository dự án giả lập chỉ phục vụ tra cứu chủ sở hữu."""

    def __init__(self, projects: list[Project] | None = None) -> None:
        """Khởi tạo với danh sách dự án có sẵn."""
        self._items: list[Project] = projects or []

    async def get_by_id(self, id: EntityID) -> Project | None:
        """Lấy dự án theo ID."""
        return next((item for item in self._items if item.id == id), None)

    async def list_by_user(self, user_id: EntityID) -> list[Project]:
        """Danh sách dự án của một người dùng."""
        return [item for item in self._items if item.user_id == user_id]

    async def save(self, entity: Project) -> Project:
        """Lưu dự án."""
        self._items.append(entity)
        return entity

    async def delete(self, id: EntityID) -> None:
        """Xóa dự án theo ID."""
        self._items = [item for item in self._items if item.id != id]


class FakeReviser(IDataModelReviser):
    """Bộ chỉnh sửa AI giả lập, trả kết quả dựng sẵn và ghi lại tham số nhận được."""

    def __init__(self, proposal: DbmlRevisionProposal | None = None) -> None:
        """Khởi tạo với kết quả muốn trả về."""
        self._proposal = proposal or DbmlRevisionProposal(
            dbml=PROPOSED_DBML, summary="Đã thêm cột rating.", changed_tables=["Dim_Driver"]
        )
        self.received_dbml: str | None = None
        self.received_instruction: str | None = None

    async def revise(self, current_dbml: str, instruction: str) -> DbmlRevisionProposal:
        """Ghi nhận tham số rồi trả kết quả dựng sẵn."""
        self.received_dbml = current_dbml
        self.received_instruction = instruction
        return self._proposal


@pytest.fixture
def owner_id() -> EntityID:
    """Định danh chủ sở hữu dự án."""
    return uuid4()


@pytest.fixture
def project(owner_id: EntityID) -> Project:
    """Dự án mẫu có chủ sở hữu xác định."""
    return Project(name="Demo", requirement="Thiết kế DWH gọi xe.", user_id=owner_id)


@pytest.fixture
def data_model(project: Project) -> DataModel:
    """Mô hình dữ liệu mẫu ở revision 3 thuộc dự án mẫu."""
    return DataModel(project_id=project.id, dbml=SAMPLE_DBML, revision=3)


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    """Đơn vị công việc giả lập dùng chung."""
    return FakeUnitOfWork()


def _build_create_service(
    data_model: DataModel,
    project: Project,
    unit_of_work: FakeUnitOfWork,
    reviser: FakeReviser | None = None,
) -> tuple[CreateChangeProposalService, FakeChangeRepository, FakeReviser]:
    """Dựng use case T-024 cùng các bản giả lập."""
    change_repository = FakeChangeRepository([])
    fake_reviser = reviser or FakeReviser()
    service = CreateChangeProposalService(
        FakeDataModelRepository([data_model]),
        change_repository,
        fake_reviser,
        FakeProjectRepository([project]),
        unit_of_work,
    )
    return service, change_repository, fake_reviser


# --- T-024: tạo đề xuất bằng AI -----------------------------------------------


@pytest.mark.asyncio
async def test_create_proposal_saves_ai_generated_dbml(
    data_model: DataModel, project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """Đề xuất tạo ra mang đúng DBML mà AI sinh và ở trạng thái PROPOSED."""
    service, change_repository, _ = _build_create_service(data_model, project, unit_of_work)

    result = await service.execute(
        ReviseDataModelInput(data_model_id=data_model.id, instruction="thêm cột rating")
    )

    assert result.proposed_dbml == PROPOSED_DBML
    assert result.status is DataModelChangeStatus.PROPOSED
    saved = await change_repository.get_by_id(result.id)
    assert saved is not None
    assert saved.proposed_dbml == PROPOSED_DBML


@pytest.mark.asyncio
async def test_create_proposal_uses_current_revision_as_base(
    data_model: DataModel, project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """base_revision phải bằng revision hiện tại của mô hình dữ liệu."""
    service, _, _ = _build_create_service(data_model, project, unit_of_work)

    result = await service.execute(
        ReviseDataModelInput(data_model_id=data_model.id, instruction="thêm cột rating")
    )

    assert result.base_revision == 3
    assert result.current_revision == 3
    assert result.is_outdated is False


@pytest.mark.asyncio
async def test_create_proposal_attributes_author_to_project_owner(
    data_model: DataModel, project: Project, owner_id: EntityID, unit_of_work: FakeUnitOfWork
) -> None:
    """Chưa có Auth nên người đứng tên đề xuất là chủ sở hữu dự án."""
    service, _, _ = _build_create_service(data_model, project, unit_of_work)

    result = await service.execute(
        ReviseDataModelInput(data_model_id=data_model.id, instruction="thêm cột rating")
    )

    assert result.user_id == owner_id


@pytest.mark.asyncio
async def test_create_proposal_passes_current_dbml_and_instruction_to_agent(
    data_model: DataModel, project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """Agent phải nhận đúng DBML hiện hành và câu lệnh của người dùng."""
    service, _, reviser = _build_create_service(data_model, project, unit_of_work)

    await service.execute(
        ReviseDataModelInput(data_model_id=data_model.id, instruction="tách Dim_Driver")
    )

    assert reviser.received_dbml == SAMPLE_DBML
    assert reviser.received_instruction == "tách Dim_Driver"


@pytest.mark.asyncio
async def test_create_proposal_returns_agent_summary(
    data_model: DataModel, project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """Lời giải thích của Agent được trả về để hiển thị trong khung chat."""
    service, _, _ = _build_create_service(data_model, project, unit_of_work)

    result = await service.execute(
        ReviseDataModelInput(data_model_id=data_model.id, instruction="thêm cột rating")
    )

    assert result.summary == "Đã thêm cột rating."


@pytest.mark.asyncio
async def test_create_proposal_commits_once(
    data_model: DataModel, project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """Luồng tạo đề xuất chỉ chốt giao dịch đúng một lần."""
    service, _, _ = _build_create_service(data_model, project, unit_of_work)

    await service.execute(
        ReviseDataModelInput(data_model_id=data_model.id, instruction="thêm cột rating")
    )

    assert unit_of_work.commit_count == 1
    assert unit_of_work.rollback_count == 0


@pytest.mark.asyncio
async def test_create_proposal_raises_when_data_model_missing(
    project: Project, unit_of_work: FakeUnitOfWork
) -> None:
    """Mô hình dữ liệu không tồn tại phải trả lỗi DATA_MODEL_NOT_FOUND."""
    service = CreateChangeProposalService(
        FakeDataModelRepository([]),
        FakeChangeRepository([]),
        FakeReviser(),
        FakeProjectRepository([project]),
        unit_of_work,
    )

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(
            ReviseDataModelInput(data_model_id=uuid4(), instruction="thêm cột rating")
        )

    assert exc_info.value.code == ErrorCode.DATA_MODEL_NOT_FOUND
    assert unit_of_work.commit_count == 0


@pytest.mark.asyncio
async def test_create_proposal_raises_when_project_missing(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Dự án chủ quản không tồn tại phải trả lỗi PROJECT_NOT_FOUND."""
    service = CreateChangeProposalService(
        FakeDataModelRepository([data_model]),
        FakeChangeRepository([]),
        FakeReviser(),
        FakeProjectRepository([]),
        unit_of_work,
    )

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(
            ReviseDataModelInput(data_model_id=data_model.id, instruction="thêm cột rating")
        )

    assert exc_info.value.code == ErrorCode.PROJECT_NOT_FOUND


# --- T-032: chấp nhận đề xuất -------------------------------------------------


@pytest.mark.asyncio
async def test_accept_applies_dbml_and_bumps_revision(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Chấp nhận thành công: DBML được thay thế và revision tăng đúng 1 đơn vị."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=3, proposed_dbml=PROPOSED_DBML
    )
    service = AcceptChangeProposalService(
        FakeDataModelRepository([data_model]), FakeChangeRepository([change]), unit_of_work
    )

    result = await service.execute(AcceptChangeProposalInput(change_id=change.id))

    assert result.dbml == PROPOSED_DBML
    assert result.revision == 4
    assert change.status is DataModelChangeStatus.ACCEPTED
    assert unit_of_work.commit_count == 1


@pytest.mark.asyncio
async def test_accept_outdated_proposal_persists_conflicted_status(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Xung đột revision phải LƯU trạng thái CONFLICTED và chốt giao dịch riêng."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=1, proposed_dbml=PROPOSED_DBML
    )
    change_repository = FakeChangeRepository([change])
    service = AcceptChangeProposalService(
        FakeDataModelRepository([data_model]), change_repository, unit_of_work
    )

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(AcceptChangeProposalInput(change_id=change.id))

    assert exc_info.value.code == ErrorCode.REVISION_CONFLICT
    saved = await change_repository.get_by_id(change.id)
    assert saved is not None
    assert saved.status is DataModelChangeStatus.CONFLICTED
    assert unit_of_work.commit_count == 1
    assert data_model.dbml == SAMPLE_DBML
    assert data_model.revision == 3


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status",
    [
        DataModelChangeStatus.ACCEPTED,
        DataModelChangeStatus.REJECTED,
        DataModelChangeStatus.CONFLICTED,
    ],
)
async def test_accept_non_proposed_status_raises_and_writes_nothing(
    data_model: DataModel, unit_of_work: FakeUnitOfWork, status: DataModelChangeStatus
) -> None:
    """Đề xuất đã xử lý trước đó không thể chấp nhận lại và không ghi gì xuống CSDL."""
    change = DataModelChange(
        data_model_id=data_model.id,
        base_revision=3,
        proposed_dbml=PROPOSED_DBML,
        status=status,
    )
    service = AcceptChangeProposalService(
        FakeDataModelRepository([data_model]), FakeChangeRepository([change]), unit_of_work
    )

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(AcceptChangeProposalInput(change_id=change.id))

    assert exc_info.value.code == ErrorCode.INVALID_PROPOSAL_STATUS_TRANSITION
    assert data_model.revision == 3
    assert unit_of_work.commit_count == 0


@pytest.mark.asyncio
async def test_accept_missing_proposal_raises_not_found(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Chấp nhận đề xuất không tồn tại phải trả lỗi PROPOSAL_NOT_FOUND."""
    service = AcceptChangeProposalService(
        FakeDataModelRepository([data_model]), FakeChangeRepository([]), unit_of_work
    )

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(AcceptChangeProposalInput(change_id=uuid4()))

    assert exc_info.value.code == ErrorCode.PROPOSAL_NOT_FOUND


# --- T-033: từ chối đề xuất ---------------------------------------------------


@pytest.mark.asyncio
async def test_reject_marks_proposal_rejected_without_touching_data_model(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Từ chối chỉ đổi trạng thái, DBML và revision của mô hình giữ nguyên."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=3, proposed_dbml=PROPOSED_DBML
    )
    service = RejectChangeProposalService(FakeChangeRepository([change]), unit_of_work)

    result = await service.execute(RejectChangeProposalInput(change_id=change.id))

    assert result.status is DataModelChangeStatus.REJECTED
    assert data_model.dbml == SAMPLE_DBML
    assert data_model.revision == 3
    assert unit_of_work.commit_count == 1


@pytest.mark.asyncio
async def test_reject_outdated_proposal_is_allowed(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Đề xuất lỗi thời vẫn từ chối được vì không cần so khớp revision."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=1, proposed_dbml=PROPOSED_DBML
    )
    service = RejectChangeProposalService(FakeChangeRepository([change]), unit_of_work)

    result = await service.execute(RejectChangeProposalInput(change_id=change.id))

    assert result.status is DataModelChangeStatus.REJECTED


@pytest.mark.asyncio
async def test_reject_already_handled_proposal_raises(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Đề xuất đã REJECTED không thể từ chối lại."""
    change = DataModelChange(
        data_model_id=data_model.id,
        base_revision=3,
        proposed_dbml=PROPOSED_DBML,
        status=DataModelChangeStatus.REJECTED,
    )
    service = RejectChangeProposalService(FakeChangeRepository([change]), unit_of_work)

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(RejectChangeProposalInput(change_id=change.id))

    assert exc_info.value.code == ErrorCode.INVALID_PROPOSAL_STATUS_TRANSITION
    assert unit_of_work.commit_count == 0


@pytest.mark.asyncio
async def test_reject_missing_proposal_raises_not_found(
    unit_of_work: FakeUnitOfWork,
) -> None:
    """Từ chối đề xuất không tồn tại phải trả lỗi PROPOSAL_NOT_FOUND."""
    service = RejectChangeProposalService(FakeChangeRepository([]), unit_of_work)

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(RejectChangeProposalInput(change_id=uuid4()))

    assert exc_info.value.code == ErrorCode.PROPOSAL_NOT_FOUND
