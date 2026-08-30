"""In-memory adapters dùng chung cho kiểm thử Project application service."""

from datetime import datetime
from types import TracebackType

from src.application.common.unit_of_work import IUnitOfWork
from src.application.projects.i_project_service import IProjectArtifactStore
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


class InMemoryProjectRepository(IProjectRepository):
    """Project repository xác định access từ owner hoặc membership được cấp."""

    def __init__(self) -> None:
        self.items: dict[EntityID, Project] = {}
        self.accessible: set[tuple[EntityID, EntityID]] = set()

    @override
    async def get_by_id(self, id: EntityID) -> Project | None:
        return self.items.get(id)

    @override
    async def list_accessible_by_user(self, user_id: EntityID) -> list[Project]:
        projects = [
            item for item in self.items.values() if item.user_id == user_id or (item.id, user_id) in self.accessible
        ]
        return sorted(projects, key=lambda item: item.updated_at, reverse=True)

    @override
    async def get_latest_activity_by_project_ids(
        self, project_ids: tuple[EntityID, ...]
    ) -> dict[EntityID, datetime]:
        return {
            project_id: self.items[project_id].updated_at
            for project_id in project_ids
            if project_id in self.items
        }

    @override
    async def save(self, entity: Project) -> Project:
        self.items[entity.id] = entity
        return entity

    @override
    async def delete(self, id: EntityID) -> None:
        self.items.pop(id, None)


class InMemoryProjectMemberRepository(IProjectMemberRepository):
    """ProjectMember repository cho authorization tests."""

    def __init__(self) -> None:
        self.items: dict[EntityID, ProjectMember] = {}

    @override
    async def get_by_id(self, id: EntityID) -> ProjectMember | None:
        return self.items.get(id)

    @override
    async def list_by_project(self, project_id: EntityID) -> list[ProjectMember]:
        return [item for item in self.items.values() if item.project_id == project_id]

    @override
    async def get_by_project_and_user(self, project_id: EntityID, user_id: EntityID) -> ProjectMember | None:
        return next(
            (item for item in self.items.values() if item.project_id == project_id and item.user_id == user_id), None
        )

    @override
    async def save(self, entity: ProjectMember) -> ProjectMember:
        self.items[entity.id] = entity
        return entity

    @override
    async def delete(self, id: EntityID) -> None:
        self.items.pop(id, None)


class InMemoryDataSourceRepository(IDataSourceRepository):
    """DataSource repository hỗ trợ truy vấn chi tiết và aggregate count."""

    def __init__(self) -> None:
        self.items: dict[EntityID, DataSource] = {}

    @override
    async def get_by_id(self, id: EntityID) -> DataSource | None:
        return self.items.get(id)

    @override
    async def list_by_project(self, project_id: EntityID) -> list[DataSource]:
        return [item for item in self.items.values() if item.project_id == project_id]

    @override
    async def count_by_project_ids(self, project_ids: tuple[EntityID, ...]) -> dict[EntityID, int]:
        return {
            project_id: sum(item.project_id == project_id for item in self.items.values())
            for project_id in project_ids
        }

    @override
    async def save(self, entity: DataSource) -> DataSource:
        self.items[entity.id] = entity
        return entity

    @override
    async def delete(self, id: EntityID) -> None:
        self.items.pop(id, None)


class InMemoryRequirementRepository(IRequirementRepository):
    """Requirement repository cho Project detail tests."""

    def __init__(self) -> None:
        self.items: dict[EntityID, Requirement] = {}

    @override
    async def get_by_id(self, id: EntityID) -> Requirement | None:
        return self.items.get(id)

    @override
    async def list_by_project(self, project_id: EntityID) -> list[Requirement]:
        return [item for item in self.items.values() if item.project_id == project_id]

    @override
    async def replace_by_project(
        self, project_id: EntityID, entities: tuple[Requirement, ...]
    ) -> list[Requirement]:
        self.items = {
            key: item for key, item in self.items.items() if item.project_id != project_id
        }
        self.items.update({item.id: item for item in entities})
        return list(entities)

    @override
    async def save(self, entity: Requirement) -> Requirement:
        self.items[entity.id] = entity
        return entity

    @override
    async def delete(self, id: EntityID) -> None:
        self.items.pop(id, None)


class InMemoryDataModelRepository(IDataModelRepository):
    """DataModel repository phục vụ project summary tests."""

    def __init__(self) -> None:
        self.items: dict[EntityID, DataModel] = {}

    @override
    async def get_by_id(self, id: EntityID) -> DataModel | None:
        return self.items.get(id)

    @override
    async def get_by_project_id(self, project_id: EntityID) -> DataModel | None:
        return next(
            (item for item in self.items.values() if item.project_id == project_id),
            None,
        )

    @override
    async def list_by_project_ids(
        self, project_ids: tuple[EntityID, ...]
    ) -> dict[EntityID, DataModel]:
        requested = set(project_ids)
        return {
            item.project_id: item
            for item in self.items.values()
            if item.project_id in requested
        }

    @override
    async def save(self, entity: DataModel) -> DataModel:
        self.items[entity.id] = entity
        return entity

    @override
    async def update_if_revision_matches(
        self, entity: DataModel, base_revision: int
    ) -> DataModel | None:
        if entity.revision != base_revision + 1:
            return None
        return await self.save(entity)

    @override
    async def delete(self, id: EntityID) -> None:
        self.items.pop(id, None)


class RecordingArtifactStore(IProjectArtifactStore):
    """Ghi nhận artifact đã được yêu cầu xóa."""

    def __init__(self) -> None:
        self.projects: list[EntityID] = []

    @override
    async def delete_project_directory(self, project_id: EntityID) -> None:
        self.projects.append(project_id)


class RecordingUnitOfWork(IUnitOfWork):
    """Ghi nhận transaction boundary."""

    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    @override
    async def commit(self) -> None:
        self.commits += 1

    @override
    async def rollback(self) -> None:
        self.rollbacks += 1

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
