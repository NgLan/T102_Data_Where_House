"""Unit tests cho Use Cases Quản lý Mô hình Dữ liệu (UpdateDataModelService & GetDataModelService)."""

from uuid import uuid4

import pytest
from src.application.data_models.dto import UpdateDataModelCommand
from src.application.data_models.GetDataModelService import GetDataModelService
from src.application.data_models.UpdateDataModelService import (
    UpdateDataModelService,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel
from src.domain.data_model.repository import IDataModelRepository
from src.domain.project.entities import Project
from src.domain.project.repository import IProjectRepository


class InMemoryProjectRepository(IProjectRepository):
    """Fake Project repository phục vụ test."""

    def __init__(self) -> None:
        self.items: dict[object, Project] = {}

    async def get_by_id(self, id: object) -> Project | None:
        return self.items.get(id)

    async def list_accessible_by_user(self, user_id: object) -> list[Project]:
        return [p for p in self.items.values() if p.user_id == user_id]

    async def save(self, entity: Project) -> Project:
        self.items[entity.id] = entity
        return entity

    async def delete(self, id: object) -> None:
        self.items.pop(id, None)


class InMemoryDataModelRepository(IDataModelRepository):
    """Fake DataModel repository phục vụ test."""

    def __init__(self) -> None:
        self.items: dict[object, DataModel] = {}

    async def get_by_id(self, id: object) -> DataModel | None:
        return self.items.get(id)

    async def get_by_project_id(self, project_id: object) -> DataModel | None:
        return next((dm for dm in self.items.values() if dm.project_id == project_id), None)

    async def save(self, entity: DataModel) -> DataModel:
        self.items[entity.id] = entity
        return entity

    async def update_if_revision_matches(
        self,
        entity: DataModel,
        base_revision: int,
    ) -> DataModel | None:
        current = self.items.get(entity.id)
        if current is None or current.revision != base_revision:
            return None
        self.items[entity.id] = entity
        return entity

    async def delete(self, id: object) -> None:
        self.items.pop(id, None)


@pytest.mark.asyncio
async def test_update_data_model_creates_initial_model() -> None:
    """Tạo mới DataModel khi project chưa có data model nào."""
    project_repo = InMemoryProjectRepository()
    data_model_repo = InMemoryDataModelRepository()

    project = Project(
        name="Dự án Phân tích",
        requirement="Yêu cầu ban đầu",
        user_id=uuid4(),
    )
    await project_repo.save(project)

    service = UpdateDataModelService(
        data_model_repo=data_model_repo,
        project_repo=project_repo,
    )

    command = UpdateDataModelCommand(
        project_id=project.id,
        dbml="Table Users { id uuid [pk] name varchar }",
    )

    result = await service.execute(command)

    assert result.project_id == project.id
    assert result.dbml == "Table Users { id uuid [pk] name varchar }"
    assert result.revision == 1


@pytest.mark.asyncio
async def test_update_data_model_updates_existing_and_increments_revision() -> None:
    """Cập nhật DBML thủ công thành công và tự động tăng revision."""
    project_repo = InMemoryProjectRepository()
    data_model_repo = InMemoryDataModelRepository()

    project = Project(
        name="Dự án Đã Có Model",
        requirement="Yêu cầu hợp lệ",
        user_id=uuid4(),
    )
    await project_repo.save(project)

    initial_model = DataModel(
        project_id=project.id,
        dbml="Table Initial { id int }",
        revision=1,
    )
    await data_model_repo.save(initial_model)

    service = UpdateDataModelService(
        data_model_repo=data_model_repo,
        project_repo=project_repo,
    )

    command = UpdateDataModelCommand(
        project_id=project.id,
        dbml="Table Updated { id int title varchar }",
        expected_revision=1,
    )

    result = await service.execute(command)

    assert result.dbml == "Table Updated { id int title varchar }"
    assert result.revision == 2

    # Lần 2: Cập nhật tiếp với revision 2
    command2 = UpdateDataModelCommand(
        project_id=project.id,
        dbml="Table Final { id int title varchar active boolean }",
        expected_revision=2,
    )
    result2 = await service.execute(command2)
    assert result2.revision == 3


@pytest.mark.asyncio
async def test_update_data_model_revision_conflict() -> None:
    """Báo lỗi xung đột khi expected_revision không khớp revision hiện tại."""
    project_repo = InMemoryProjectRepository()
    data_model_repo = InMemoryDataModelRepository()

    project = Project(name="Dự án Conflict", requirement="Yêu cầu hợp lệ", user_id=uuid4())
    await project_repo.save(project)

    initial_model = DataModel(
        project_id=project.id,
        dbml="Table Initial { id int }",
        revision=5,
    )
    await data_model_repo.save(initial_model)

    service = UpdateDataModelService(
        data_model_repo=data_model_repo,
        project_repo=project_repo,
    )

    command = UpdateDataModelCommand(
        project_id=project.id,
        dbml="Table Modified { id int }",
        expected_revision=4,  # Sai revision
    )

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(command)

    assert exc_info.value.code == ErrorCode.REVISION_CONFLICT


@pytest.mark.asyncio
async def test_update_data_model_empty_dbml_rejected() -> None:
    """Nội dung DBML rỗng bị từ chối với INVALID_DBML_CONTENT."""
    project_repo = InMemoryProjectRepository()
    data_model_repo = InMemoryDataModelRepository()

    project = Project(name="Dự án Empty", requirement="Yêu cầu hợp lệ", user_id=uuid4())
    await project_repo.save(project)

    service = UpdateDataModelService(
        data_model_repo=data_model_repo,
        project_repo=project_repo,
    )

    command = UpdateDataModelCommand(
        project_id=project.id,
        dbml="   ",
    )

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(command)

    assert exc_info.value.code == ErrorCode.INVALID_DBML_CONTENT


@pytest.mark.asyncio
async def test_update_data_model_project_not_found() -> None:
    """Báo lỗi PROJECT_NOT_FOUND khi project_id không tồn tại."""
    project_repo = InMemoryProjectRepository()
    data_model_repo = InMemoryDataModelRepository()

    service = UpdateDataModelService(
        data_model_repo=data_model_repo,
        project_repo=project_repo,
    )

    command = UpdateDataModelCommand(
        project_id=uuid4(),
        dbml="Table Users { id uuid }",
    )

    with pytest.raises(BusinessException) as exc_info:
        await service.execute(command)

    assert exc_info.value.code == ErrorCode.PROJECT_NOT_FOUND


@pytest.mark.asyncio
async def test_get_data_model_service() -> None:
    """Kiểm tra truy vấn DataModel của dự án."""
    project_repo = InMemoryProjectRepository()
    data_model_repo = InMemoryDataModelRepository()

    project = Project(name="Dự án Query", requirement="Yêu cầu hợp lệ", user_id=uuid4())
    await project_repo.save(project)

    service = GetDataModelService(
        data_model_repo=data_model_repo,
        project_repo=project_repo,
    )

    # Khi chưa có model -> trả về None
    res_empty = await service.execute(project.id)
    assert res_empty is None

    # Sau khi có model
    dm = DataModel(project_id=project.id, dbml="Table Test { id int }", revision=1)
    await data_model_repo.save(dm)

    res_found = await service.execute(project.id)
    assert res_found is not None
    assert res_found.dbml == "Table Test { id int }"
    assert res_found.revision == 1
