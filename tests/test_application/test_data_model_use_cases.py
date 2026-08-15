"""Kiểm thử các Use Case thuộc miền Mô hình Dữ liệu (T-030, T-031)."""

from uuid import UUID, uuid4

import pytest
from src.application.data_models.dto import (
    GenerateDdlInput,
    GetChangeProposalInput,
    GetDataModelInput,
    ListChangeProposalsInput,
)
from src.application.data_models.generate_ddl import GenerateDdlService
from src.application.data_models.get_change_proposal import GetChangeProposalService
from src.application.data_models.get_data_model import GetDataModelService
from src.application.data_models.list_change_proposals import ListChangeProposalsService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.data_model.enums import DataModelChangeStatus, SqlDialect
from src.domain.data_model.repository import (
    IDataModelChangeRepository,
    IDataModelRepository,
)
from src.domain.shared.types import EntityID
from src.infrastructure.codegen.ddl_generator import DbmlDdlGenerator

SAMPLE_DBML = """Table Dim_Driver {
  driver_key int [pk]
  full_name varchar(100)
}"""

PROPOSED_DBML = """Table Dim_Driver {
  driver_key int [pk]
  full_name varchar(100)
  rating decimal(3,2)
}"""


class FakeDataModelRepository(IDataModelRepository):
    """Repository mô hình dữ liệu giả lập lưu trong bộ nhớ phục vụ kiểm thử."""

    def __init__(self, data_models: list[DataModel] | None = None) -> None:
        """Khởi tạo với danh sách mô hình dữ liệu có sẵn."""
        self._items: list[DataModel] = data_models or []

    async def get_by_id(self, id: EntityID) -> DataModel | None:
        """Lấy mô hình dữ liệu theo ID."""
        return next((item for item in self._items if item.id == id), None)

    async def get_by_project_id(self, project_id: EntityID) -> DataModel | None:
        """Lấy mô hình dữ liệu theo dự án."""
        return next((item for item in self._items if item.project_id == project_id), None)

    async def save(self, entity: DataModel) -> DataModel:
        """Lưu mô hình dữ liệu."""
        self._items.append(entity)
        return entity

    async def delete(self, id: EntityID) -> None:
        """Xóa mô hình dữ liệu theo ID."""
        self._items = [item for item in self._items if item.id != id]


class FakeChangeRepository(IDataModelChangeRepository):
    """Repository đề xuất thay đổi giả lập lưu trong bộ nhớ phục vụ kiểm thử."""

    def __init__(self, changes: list[DataModelChange] | None = None) -> None:
        """Khởi tạo với danh sách đề xuất thay đổi có sẵn."""
        self._items: list[DataModelChange] = changes or []

    async def get_by_id(self, id: EntityID) -> DataModelChange | None:
        """Lấy đề xuất thay đổi theo ID."""
        return next((item for item in self._items if item.id == id), None)

    async def list_by_data_model(self, data_model_id: EntityID) -> list[DataModelChange]:
        """Danh sách đề xuất thay đổi của một mô hình dữ liệu."""
        return [item for item in self._items if item.data_model_id == data_model_id]

    async def save(self, entity: DataModelChange) -> DataModelChange:
        """Lưu đề xuất thay đổi."""
        self._items.append(entity)
        return entity

    async def delete(self, id: EntityID) -> None:
        """Xóa đề xuất thay đổi theo ID."""
        self._items = [item for item in self._items if item.id != id]


@pytest.fixture
def project_id() -> UUID:
    """Định danh dự án dùng chung cho các bài kiểm thử."""
    return uuid4()


@pytest.fixture
def data_model(project_id: UUID) -> DataModel:
    """Mô hình dữ liệu mẫu ở revision 3."""
    return DataModel(project_id=project_id, dbml=SAMPLE_DBML, revision=3)


# --- GetDataModelService ------------------------------------------------------


@pytest.mark.asyncio
async def test_get_data_model_returns_current_dbml_and_revision(
    data_model: DataModel, project_id: UUID
) -> None:
    """Trả về đúng nội dung DBML và revision hiện hành của dự án."""
    service = GetDataModelService(FakeDataModelRepository([data_model]))

    result = await service.execute(GetDataModelInput(project_id=project_id))

    assert result.id == data_model.id
    assert result.project_id == project_id
    assert result.dbml == SAMPLE_DBML
    assert result.revision == 3


@pytest.mark.asyncio
async def test_get_data_model_raises_when_project_has_no_model() -> None:
    """Dự án chưa có mô hình dữ liệu phải trả lỗi DATA_MODEL_NOT_FOUND."""
    service = GetDataModelService(FakeDataModelRepository([]))

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(GetDataModelInput(project_id=uuid4()))

    assert exc_info.value.code == ErrorCode.DATA_MODEL_NOT_FOUND


# --- GenerateDdlService -------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("dialect", list(SqlDialect))
async def test_generate_ddl_returns_script_for_each_dialect(
    data_model: DataModel, dialect: SqlDialect
) -> None:
    """Sinh mã DDL thành công cho cả ba hệ quản trị CSDL được hỗ trợ."""
    service = GenerateDdlService(FakeDataModelRepository([data_model]), DbmlDdlGenerator())

    payload = GenerateDdlInput(data_model_id=data_model.id, dialect=dialect)
    result = await service.execute(payload)

    assert result.dialect is dialect
    assert result.table_count == 1
    assert result.revision == 3
    assert "Dim_Driver" in result.ddl
    assert result.schema_name == "sandbox_dwh"


@pytest.mark.asyncio
async def test_generate_ddl_raises_when_data_model_missing() -> None:
    """Sinh DDL cho mô hình không tồn tại phải trả lỗi DATA_MODEL_NOT_FOUND."""
    service = GenerateDdlService(FakeDataModelRepository([]), DbmlDdlGenerator())

    payload = GenerateDdlInput(data_model_id=uuid4(), dialect=SqlDialect.POSTGRESQL)
    with pytest.raises(BusinessException) as exc_info:
        await service.execute(payload)

    assert exc_info.value.code == ErrorCode.DATA_MODEL_NOT_FOUND


# --- ListChangeProposalsService -----------------------------------------------


@pytest.mark.asyncio
async def test_list_change_proposals_filters_by_status(data_model: DataModel) -> None:
    """Lọc đúng theo trạng thái đề xuất khi có tham số `status`."""
    proposed = DataModelChange(
        data_model_id=data_model.id, base_revision=3, proposed_dbml=PROPOSED_DBML
    )
    rejected = DataModelChange(
        data_model_id=data_model.id,
        base_revision=2,
        proposed_dbml=PROPOSED_DBML,
        status=DataModelChangeStatus.REJECTED,
    )
    service = ListChangeProposalsService(
        FakeDataModelRepository([data_model]),
        FakeChangeRepository([proposed, rejected]),
    )

    payload = ListChangeProposalsInput(
        data_model_id=data_model.id, status=DataModelChangeStatus.PROPOSED
    )
    results = await service.execute(payload)

    assert [item.id for item in results] == [proposed.id]


@pytest.mark.asyncio
async def test_list_change_proposals_returns_all_without_filter(
    data_model: DataModel,
) -> None:
    """Không truyền `status` thì trả về toàn bộ đề xuất của mô hình dữ liệu."""
    changes = [
        DataModelChange(data_model_id=data_model.id, base_revision=3, proposed_dbml=PROPOSED_DBML),
        DataModelChange(data_model_id=data_model.id, base_revision=2, proposed_dbml=PROPOSED_DBML),
    ]
    service = ListChangeProposalsService(
        FakeDataModelRepository([data_model]), FakeChangeRepository(changes)
    )

    results = await service.execute(ListChangeProposalsInput(data_model_id=data_model.id))

    assert len(results) == 2


@pytest.mark.asyncio
async def test_list_change_proposals_raises_when_data_model_missing() -> None:
    """Liệt kê đề xuất của mô hình không tồn tại phải trả lỗi DATA_MODEL_NOT_FOUND."""
    service = ListChangeProposalsService(FakeDataModelRepository([]), FakeChangeRepository([]))

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(ListChangeProposalsInput(data_model_id=uuid4()))

    assert exc_info.value.code == ErrorCode.DATA_MODEL_NOT_FOUND


# --- GetChangeProposalService (UC6.1) -----------------------------------------


@pytest.mark.asyncio
async def test_get_change_proposal_returns_both_dbml_versions(
    data_model: DataModel,
) -> None:
    """Trả về đồng thời DBML đề xuất và DBML hiện hành để dựng khung so sánh."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=3, proposed_dbml=PROPOSED_DBML
    )
    service = GetChangeProposalService(
        FakeDataModelRepository([data_model]), FakeChangeRepository([change])
    )

    result = await service.execute(GetChangeProposalInput(change_id=change.id))

    assert result.proposed_dbml == PROPOSED_DBML
    assert result.current_dbml == SAMPLE_DBML
    assert result.base_revision == 3
    assert result.current_revision == 3
    assert result.status is DataModelChangeStatus.PROPOSED


@pytest.mark.asyncio
async def test_get_change_proposal_is_not_outdated_when_revision_matches(
    data_model: DataModel,
) -> None:
    """base_revision khớp revision hiện tại thì đề xuất chưa lỗi thời."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=3, proposed_dbml=PROPOSED_DBML
    )
    service = GetChangeProposalService(
        FakeDataModelRepository([data_model]), FakeChangeRepository([change])
    )

    result = await service.execute(GetChangeProposalInput(change_id=change.id))

    assert result.is_outdated is False


@pytest.mark.asyncio
async def test_get_change_proposal_is_outdated_when_revision_diverged(
    data_model: DataModel,
) -> None:
    """base_revision lệch revision hiện tại thì đề xuất đã lỗi thời (Edge case 1 & 5)."""
    change = DataModelChange(
        data_model_id=data_model.id, base_revision=1, proposed_dbml=PROPOSED_DBML
    )
    service = GetChangeProposalService(
        FakeDataModelRepository([data_model]), FakeChangeRepository([change])
    )

    result = await service.execute(GetChangeProposalInput(change_id=change.id))

    assert result.is_outdated is True
    assert result.base_revision == 1
    assert result.current_revision == 3


@pytest.mark.asyncio
async def test_get_change_proposal_raises_when_proposal_missing(
    data_model: DataModel,
) -> None:
    """Đề xuất không tồn tại phải trả lỗi PROPOSAL_NOT_FOUND."""
    service = GetChangeProposalService(
        FakeDataModelRepository([data_model]), FakeChangeRepository([])
    )

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(GetChangeProposalInput(change_id=uuid4()))

    assert exc_info.value.code == ErrorCode.PROPOSAL_NOT_FOUND


@pytest.mark.asyncio
async def test_get_change_proposal_raises_when_parent_data_model_missing() -> None:
    """Đề xuất trỏ tới mô hình dữ liệu đã bị xóa phải trả lỗi DATA_MODEL_NOT_FOUND."""
    change = DataModelChange(
        data_model_id=uuid4(), base_revision=1, proposed_dbml=PROPOSED_DBML
    )
    service = GetChangeProposalService(
        FakeDataModelRepository([]), FakeChangeRepository([change])
    )

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(GetChangeProposalInput(change_id=change.id))

    assert exc_info.value.code == ErrorCode.DATA_MODEL_NOT_FOUND
