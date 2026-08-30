"""Bản giả lập trong bộ nhớ cho Unit of Work và các Repository, dùng chung cho test."""

from datetime import datetime
from types import TracebackType

from src.application.common.unit_of_work import IUnitOfWork
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.i_analytical_requirement_repository import (
    IAnalyticalRequirementRepository,
)
from src.domain.data_model.entities import DataModel
from src.domain.data_model.i_data_model_repository import IDataModelRepository
from src.domain.data_source.entities import DataSource
from src.domain.data_source.i_data_source_repository import IDataSourceRepository
from src.domain.project.entities import Project, ProjectMember
from src.domain.project.i_project_member_repository import IProjectMemberRepository
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.requirement.entities import Requirement
from src.domain.requirement.i_requirement_repository import IRequirementRepository
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

    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Rollback khi khối `async with` thoát ra do ngoại lệ, giống bản thật."""
        if exc_type is not None:
            await self.rollback()


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
    async def list_accessible_by_user(self, user_id: EntityID) -> list[Project]:
        """Danh sách dự án người dùng có quyền truy cập."""
        return [item for item in self._items if item.user_id == user_id]

    @override
    async def get_latest_activity_by_project_ids(
        self, project_ids: tuple[EntityID, ...]
    ) -> dict[EntityID, datetime]:
        requested = set(project_ids)
        return {
            item.id: item.updated_at
            for item in self._items
            if item.id in requested
        }


class FakeProjectMemberRepository(_InMemoryRepository, IProjectMemberRepository):
    """Repository membership dự án giả lập."""

    @override
    async def list_by_project(self, project_id: EntityID) -> list[ProjectMember]:
        return [item for item in self._items if item.project_id == project_id]

    @override
    async def get_by_project_and_user(
        self, project_id: EntityID, user_id: EntityID
    ) -> ProjectMember | None:
        return next(
            (
                item
                for item in self._items
                if item.project_id == project_id and item.user_id == user_id
            ),
            None,
        )


class FakeRequirementRepository(_InMemoryRepository, IRequirementRepository):
    """Repository yêu cầu nghiệp vụ giả lập."""

    @override
    async def list_by_project(self, project_id: EntityID) -> list[Requirement]:
        """Danh sách yêu cầu thuộc một dự án."""
        return [item for item in self._items if item.project_id == project_id]

    @override
    async def replace_by_project(
        self, project_id: EntityID, entities: tuple[Requirement, ...]
    ) -> list[Requirement]:
        """Thay toàn bộ yêu cầu của dự án."""
        self._items = [item for item in self._items if item.project_id != project_id]
        self._items.extend(entities)
        return list(entities)


class FakeDataSourceRepository(_InMemoryRepository, IDataSourceRepository):
    """Repository nguồn dữ liệu giả lập."""

    @override
    async def list_by_project(self, project_id: EntityID) -> list[DataSource]:
        """Danh sách nguồn dữ liệu thuộc một dự án."""
        return [item for item in self._items if item.project_id == project_id]

    @override
    async def count_by_project_ids(
        self, project_ids: tuple[EntityID, ...]
    ) -> dict[EntityID, int]:
        """Đếm số nguồn dữ liệu của từng dự án."""
        return {
            project_id: sum(item.project_id == project_id for item in self._items)
            for project_id in project_ids
        }


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

    @override
    async def list_by_project(
        self, project_id: EntityID
    ) -> list[AnalyticalRequirement]:
        """Fake không có join nên lọc qua tập requirement ID được gắn bởi test."""
        requirement_ids = getattr(self, "project_requirement_ids", {}).get(project_id, set())
        return [item for item in self._items if item.requirement_id in requirement_ids]

    @override
    async def replace_by_project(
        self,
        project_id: EntityID,
        entities: tuple[AnalyticalRequirement, ...],
    ) -> list[AnalyticalRequirement]:
        """Thay tập analytical và ghi mapping phục vụ list_by_project."""
        mapping = getattr(self, "project_requirement_ids", {})
        old_ids = mapping.get(project_id, set())
        self._items = [item for item in self._items if item.requirement_id not in old_ids]
        new_ids = {item.requirement_id for item in entities}
        mapping[project_id] = new_ids
        self.project_requirement_ids = mapping
        self._items.extend(entities)
        return list(entities)


class FakeDataModelRepository(_InMemoryRepository, IDataModelRepository):
    """Repository mô hình dữ liệu giả lập."""

    @override
    async def get_by_project_id(self, project_id: EntityID) -> DataModel | None:
        """Mô hình dữ liệu của một dự án."""
        return next((item for item in self._items if item.project_id == project_id), None)

    @override
    async def list_by_project_ids(
        self, project_ids: list[EntityID]
    ) -> dict[EntityID, DataModel]:
        """Các mô hình dữ liệu được lập chỉ mục theo dự án."""
        requested = set(project_ids)
        return {
            item.project_id: item
            for item in self._items
            if item.project_id in requested
        }

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
