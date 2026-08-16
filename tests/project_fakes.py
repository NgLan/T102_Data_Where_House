"""In-memory adapters dùng chung cho kiểm thử Project application service."""

from src.application.common.unit_of_work import IUnitOfWork
from src.application.projects.i_project_artifact_store import IProjectArtifactStore
from src.domain.data_source.entities import DataSource
from src.domain.data_source.repository import IDataSourceRepository
from src.domain.project.entities import Project, ProjectMember
from src.domain.project.repository import IProjectMemberRepository, IProjectRepository
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


class RecordingArtifactStore(IProjectArtifactStore):
    """Ghi nhận artifact đã được yêu cầu xóa."""

    def __init__(self) -> None:
        self.files: list[str] = []
        self.projects: list[EntityID] = []

    @override
    async def delete_file(self, file_path: str) -> None:
        self.files.append(file_path)

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
