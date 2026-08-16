"""Kiểm thử Use Case chấp nhận (T-032) và từ chối (T-033) đề xuất thay đổi."""

from types import TracebackType
from uuid import uuid4

import pytest
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.accept_change_proposal import AcceptChangeProposalService
from src.application.data_models.dto import (
    AcceptChangeProposalInput,
    RejectChangeProposalInput,
)
from src.application.data_models.reject_change_proposal import RejectChangeProposalService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.enums import DataModelChangeStatus

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


@pytest.fixture
def data_model() -> DataModel:
    """Mô hình dữ liệu mẫu đang ở revision 3."""
    return DataModel(project_id=uuid4(), dbml=SAMPLE_DBML, revision=3)


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    """Đơn vị công việc giả lập dùng chung cho các bài kiểm thử."""
    return FakeUnitOfWork()


def _build_accept_service(
    data_model: DataModel,
    change: DataModelChange,
    unit_of_work: FakeUnitOfWork,
) -> tuple[AcceptChangeProposalService, FakeChangeRepository]:
    """Dựng use case Accept cùng repository giả lập đã nạp sẵn dữ liệu."""
    change_repository = FakeChangeRepository([change])
    service = AcceptChangeProposalService(
        FakeDataModelRepository([data_model]), change_repository, unit_of_work
    )
    return service, change_repository


# --- T-032: Accept ------------------------------------------------------------


@pytest.mark.asyncio
async def test_accept_applies_proposed_dbml_and_bumps_revision(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Chấp nhận thành công: DBML được thay thế và revision tăng đúng 1 đơn vị."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=3, proposed_dbml=PROPOSED_DBML
    )
    service, _ = _build_accept_service(data_model, change, unit_of_work)

    result = await service.execute(AcceptChangeProposalInput(change_id=change.id))

    assert result.dbml == PROPOSED_DBML
    assert result.revision == 4
    assert result.id == data_model.id


@pytest.mark.asyncio
async def test_accept_marks_proposal_as_accepted(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Chấp nhận thành công thì đề xuất chuyển sang trạng thái ACCEPTED."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=3, proposed_dbml=PROPOSED_DBML
    )
    service, change_repository = _build_accept_service(data_model, change, unit_of_work)

    await service.execute(AcceptChangeProposalInput(change_id=change.id))

    saved = await change_repository.get_by_id(change.id)
    assert saved is not None
    assert saved.status is DataModelChangeStatus.ACCEPTED


@pytest.mark.asyncio
async def test_accept_commits_transaction_exactly_once(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Luồng chấp nhận thành công chỉ chốt giao dịch đúng một lần."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=3, proposed_dbml=PROPOSED_DBML
    )
    service, _ = _build_accept_service(data_model, change, unit_of_work)

    await service.execute(AcceptChangeProposalInput(change_id=change.id))

    assert unit_of_work.commit_count == 1
    assert unit_of_work.rollback_count == 0


@pytest.mark.asyncio
async def test_accept_outdated_proposal_raises_revision_conflict(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """base_revision lệch revision hiện tại phải trả lỗi REVISION_CONFLICT."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=1, proposed_dbml=PROPOSED_DBML
    )
    service, _ = _build_accept_service(data_model, change, unit_of_work)

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(AcceptChangeProposalInput(change_id=change.id))

    assert exc_info.value.code == ErrorCode.REVISION_CONFLICT


@pytest.mark.asyncio
async def test_accept_outdated_proposal_persists_conflicted_status(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Xung đột revision phải LƯU trạng thái CONFLICTED và chốt giao dịch riêng.

    Đây là hành vi cốt lõi của T-032: tầng Domain đánh dấu CONFLICTED rồi mới ném lỗi,
    nếu không chốt giao dịch riêng thì việc đánh dấu sẽ mất trắng khi ngoại lệ lan lên.
    """
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=1, proposed_dbml=PROPOSED_DBML
    )
    service, change_repository = _build_accept_service(data_model, change, unit_of_work)

    with pytest.raises(BusinessException):
        await service.execute(AcceptChangeProposalInput(change_id=change.id))

    saved = await change_repository.get_by_id(change.id)
    assert saved is not None
    assert saved.status is DataModelChangeStatus.CONFLICTED
    assert unit_of_work.commit_count == 1


@pytest.mark.asyncio
async def test_accept_outdated_proposal_leaves_data_model_untouched(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Xung đột revision không được làm thay đổi nội dung mô hình dữ liệu."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=1, proposed_dbml=PROPOSED_DBML
    )
    service, _ = _build_accept_service(data_model, change, unit_of_work)

    with pytest.raises(BusinessException):
        await service.execute(AcceptChangeProposalInput(change_id=change.id))

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
async def test_accept_non_proposed_status_raises_invalid_transition(
    data_model: DataModel, unit_of_work: FakeUnitOfWork, status: DataModelChangeStatus
) -> None:
    """Đề xuất đã được xử lý trước đó không thể chấp nhận lại."""
    change = DataModelChange(
        data_model_id=data_model.id,
        base_revision=3,
        proposed_dbml=PROPOSED_DBML,
        status=status,
    )
    service, _ = _build_accept_service(data_model, change, unit_of_work)

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


@pytest.mark.asyncio
async def test_accept_missing_parent_data_model_raises_not_found(
    unit_of_work: FakeUnitOfWork,
) -> None:
    """Đề xuất trỏ tới mô hình dữ liệu đã bị xóa phải trả lỗi DATA_MODEL_NOT_FOUND."""
    change = DataModelChange(
        data_model_id=uuid4(), base_revision=1, proposed_dbml=PROPOSED_DBML
    )
    service = AcceptChangeProposalService(
        FakeDataModelRepository([]), FakeChangeRepository([change]), unit_of_work
    )

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(AcceptChangeProposalInput(change_id=change.id))

    assert exc_info.value.code == ErrorCode.DATA_MODEL_NOT_FOUND


# --- T-033: Reject ------------------------------------------------------------


@pytest.mark.asyncio
async def test_reject_marks_proposal_as_rejected(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Từ chối thành công thì đề xuất chuyển sang trạng thái REJECTED."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=3, proposed_dbml=PROPOSED_DBML
    )
    service = RejectChangeProposalService(FakeChangeRepository([change]), unit_of_work)

    result = await service.execute(RejectChangeProposalInput(change_id=change.id))

    assert result.status is DataModelChangeStatus.REJECTED
    assert result.id == change.id
    assert unit_of_work.commit_count == 1


@pytest.mark.asyncio
async def test_reject_leaves_data_model_unchanged(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Từ chối không đụng tới nội dung DBML và revision của mô hình dữ liệu."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=3, proposed_dbml=PROPOSED_DBML
    )
    service = RejectChangeProposalService(FakeChangeRepository([change]), unit_of_work)

    await service.execute(RejectChangeProposalInput(change_id=change.id))

    assert data_model.dbml == SAMPLE_DBML
    assert data_model.revision == 3


@pytest.mark.asyncio
async def test_reject_outdated_proposal_is_still_allowed(
    data_model: DataModel, unit_of_work: FakeUnitOfWork
) -> None:
    """Đề xuất đã lỗi thời vẫn được phép từ chối vì không cần so khớp revision."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=1, proposed_dbml=PROPOSED_DBML
    )
    service = RejectChangeProposalService(FakeChangeRepository([change]), unit_of_work)

    result = await service.execute(RejectChangeProposalInput(change_id=change.id))

    assert result.status is DataModelChangeStatus.REJECTED


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status",
    [
        DataModelChangeStatus.ACCEPTED,
        DataModelChangeStatus.REJECTED,
        DataModelChangeStatus.CONFLICTED,
    ],
)
async def test_reject_non_proposed_status_raises_invalid_transition(
    data_model: DataModel, unit_of_work: FakeUnitOfWork, status: DataModelChangeStatus
) -> None:
    """Đề xuất đã được xử lý trước đó không thể từ chối lại."""
    change = DataModelChange(
        data_model_id=data_model.id,
        base_revision=3,
        proposed_dbml=PROPOSED_DBML,
        status=status,
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
