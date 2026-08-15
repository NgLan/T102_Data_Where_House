"""Unit tests cho UC5.1.3 chỉnh sửa Data Model trực quan."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_models.data_model_service import DataModelService
from src.application.data_models.input import UpdateDataModelInput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel
from src.domain.data_model.repository import IDataModelRepository


def test_data_model_accepts_structured_dbml() -> None:
    """DBML hợp lệ hỗ trợ composite PK, default, unique và note."""
    dbml = r"""
    Table order_items {
      order_id uuid [pk, not null]
      product_id uuid [pk, not null]
      quantity integer [not null, default: 1]
      description varchar(255) [unique, note: 'Mô tả']
      owner_name varchar(255) [note: 'O\'Brien']
    }
    """

    data_model = DataModel(project_id=uuid4(), dbml=dbml)

    assert data_model.revision == 1


def test_data_model_accepts_custom_dbml_data_type() -> None:
    """DBML cho phép custom type thay vì áp một whitelist theo database cụ thể."""
    data_model = DataModel(
        project_id=uuid4(),
        dbml="Table users {\n amount money_domain\n}",
    )

    assert data_model.revision == 1


@pytest.mark.parametrize(
    "dbml",
    [
        "Table users {\n amount integer [default:]\n}",
        "Table users {\n id uuid\n",
        "Table {\n id uuid\n}",
    ],
)
def test_data_model_rejects_invalid_dbml(dbml: str) -> None:
    """Backend không tin DBML từ Frontend và từ chối cú pháp không hợp lệ."""
    with pytest.raises(BusinessException) as exc_info:
        DataModel(project_id=uuid4(), dbml=dbml)

    assert exc_info.value.code == ErrorCode.INVALID_DBML_CONTENT


@pytest.mark.asyncio
async def test_update_service_increments_revision_and_commits() -> None:
    """Service lưu snapshot mới, tăng đúng một revision và commit transaction."""
    current = DataModel(project_id=uuid4(), dbml="Table users { id uuid }", revision=3)
    repository = AsyncMock(spec=IDataModelRepository)
    unit_of_work = AsyncMock(spec=IUnitOfWork)
    repository.get_by_project_id.return_value = current
    repository.update_if_revision_matches.return_value = current
    service = DataModelService(repository, unit_of_work)
    command = create_command(current, "Table users {\n id uuid [pk]\n}", 3)

    result = await service.update_data_model(command)

    assert result.revision == 4
    repository.update_if_revision_matches.assert_awaited_once_with(current, 3)
    unit_of_work.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_service_rejects_atomic_race_conflict() -> None:
    """Atomic update trả rỗng phải thành conflict và tuyệt đối không commit."""
    current = DataModel(project_id=uuid4(), dbml="Table users { id uuid }", revision=3)
    repository = AsyncMock(spec=IDataModelRepository)
    unit_of_work = AsyncMock(spec=IUnitOfWork)
    repository.get_by_project_id.return_value = current
    repository.update_if_revision_matches.return_value = None
    service = DataModelService(repository, unit_of_work)
    command = create_command(current, "Table users {\n id uuid [pk]\n}", 3)

    with pytest.raises(BusinessException) as exc_info:
        await service.update_data_model(command)

    assert exc_info.value.code == ErrorCode.REVISION_CONFLICT
    unit_of_work.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_service_rejects_stale_base_revision() -> None:
    """Revision cũ bị từ chối trước persistence và không ghi đè snapshot mới hơn."""
    current = DataModel(project_id=uuid4(), dbml="Table users { id uuid }", revision=4)
    repository = AsyncMock(spec=IDataModelRepository)
    unit_of_work = AsyncMock(spec=IUnitOfWork)
    repository.get_by_project_id.return_value = current
    service = DataModelService(repository, unit_of_work)
    command = create_command(current, "Table users {\n id uuid [pk]\n}", 3)

    with pytest.raises(BusinessException) as exc_info:
        await service.update_data_model(command)

    assert exc_info.value.code == ErrorCode.REVISION_CONFLICT
    repository.update_if_revision_matches.assert_not_awaited()


def create_command(data_model: DataModel, dbml: str, base_revision: int) -> UpdateDataModelInput:
    """Tạo command cập nhật hợp lệ cho unit tests."""
    return UpdateDataModelInput(
        project_id=data_model.project_id,
        data_model_id=data_model.id,
        dbml=dbml,
        base_revision=base_revision,
    )
