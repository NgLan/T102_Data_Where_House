"""Bản giả lập trong bộ nhớ cho Unit of Work và các Repository, dùng chung cho test."""

from src.application.common.unit_of_work import IUnitOfWork
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.repository import IAnalyticalRequirementRepository
from src.domain.data_model.entities import DataModel
from src.domain.data_model.repository import IDataModelRepository
from src.domain.data_source.entities import DataSource
from src.domain.data_source.repository import IDataSourceRepository
from src.domain.project.entities import Project
from src.domain.project.repository import IProjectRepository
from src.domain.requirement.entities import Requirement
from src.domain.requirement.repository import IRequirementRepository
from src.domain.shared.types import EntityID
from typing_extensions import override


class FakeUnitOfWork(IUnitOfWork):
    """Đơn vị công việc giả lập, đếm số lần chốt và hủy giao dịch."""

    def __init__(self) -> None:
        """Khởi tạo bộ đếm giao dịch."""
        self.commit_count: int = 0
        self.rollback_count: int = 0

    @override
    async def commit(self) -> None:
        """Ghi nhận một lần chốt giao dịch."""
        self.commit_count += 1

    @override
    async def rollback(self) -> None:
        """Ghi nhận một lần hủy giao dịch."""
        self.rollback_count += 1


class _InMemoryRepository:
    """Kho lưu trữ trong bộ nhớ dùng lại cho mọi repository giả lập."""

    def __init__(self, items: list | None = None) -> None:
        """Khởi tạo với danh sách thực thể có sẵn."""
        self._items: list = list(items or [])

    async def get_by_id(self, entity_id: EntityID):
        """Lấy thực thể theo ID."""
        return next((item for item in self._items if item.id == entity_id), None)

    async def save(self, entity):
        """Lưu mới hoặc thay thế thực thể theo ID."""
        self._items = [item for item in self._items if item.id != entity.id]
        self._items.append(entity)
        return entity

    async def delete(self, entity_id: EntityID) -> bool:
        """Xóa thực thể theo ID."""
        remaining = [item for item in self._items if item.id != entity_id]
        removed = len(remaining) != len(self._items)
        self._items = remaining
        return removed


class FakeProjectRepository(_InMemoryRepository, IProjectRepository):
    """Repository dự án giả lập."""

    @override
    async def list_by_user(self, user_id: EntityID) -> list[Project]:
        """Danh sách dự án của một người dùng."""
        return [item for item in self._items if item.user_id == user_id]


class FakeRequirementRepository(_InMemoryRepository, IRequirementRepository):
    """Repository yêu cầu nghiệp vụ giả lập."""

    @override
    async def list_by_project(self, project_id: EntityID) -> list[Requirement]:
        """Danh sách yêu cầu thuộc một dự án."""
        return [item for item in self._items if item.project_id == project_id]


class FakeDataSourceRepository(_InMemoryRepository, IDataSourceRepository):
    """Repository nguồn dữ liệu giả lập."""

    @override
    async def list_by_project(self, project_id: EntityID) -> list[DataSource]:
        """Danh sách nguồn dữ liệu thuộc một dự án."""
        return [item for item in self._items if item.project_id == project_id]


class FakeAnalyticalRequirementRepository(
    _InMemoryRepository, IAnalyticalRequirementRepository
):
    """Repository yêu cầu phân tích giả lập."""

    @override
    async def get_by_requirement_id(
        self, requirement_id: EntityID
    ) -> list[AnalyticalRequirement]:
        """Danh sách chi tiết phân tích theo ID yêu cầu gốc."""
        return [item for item in self._items if item.requirement_id == requirement_id]


class FakeDataModelRepository(_InMemoryRepository, IDataModelRepository):
    """Repository mô hình dữ liệu giả lập."""

    @override
    async def get_by_project_id(self, project_id: EntityID) -> DataModel | None:
        """Mô hình dữ liệu của một dự án."""
        return next((item for item in self._items if item.project_id == project_id), None)

    @override
    async def update_if_revision_matches(
        self, entity: DataModel, base_revision: int
    ) -> DataModel | None:
        """Cập nhật khi revision hiện tại vẫn khớp base revision.

        Thực thể đã được `update_dbml()` tăng revision trước khi gọi vào đây, nên bản ghi
        hợp lệ sẽ có `revision == base_revision + 1`.
        """
        if entity.revision != base_revision + 1:
            return None
        return await self.save(entity)
