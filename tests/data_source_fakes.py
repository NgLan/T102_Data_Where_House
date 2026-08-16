"""In-memory adapters cho Data Source service tests."""

from src.application.common.unit_of_work import IUnitOfWork
from src.domain.data_source.entities import DataSource
from src.domain.data_source.repository import IDataSourceRepository
from src.domain.project.entities import Project, ProjectMember
from src.domain.project.repository import IProjectMemberRepository, IProjectRepository
from src.domain.shared.types import EntityID


class InMemoryDataSources(IDataSourceRepository):
    """Lưu DataSource trong bộ nhớ."""

    def __init__(self) -> None:
        self.items: dict[EntityID, DataSource] = {}

    async def get_by_id(self, entity_id: EntityID) -> DataSource | None:
        return self.items.get(entity_id)

    async def list_by_project(self, project_id: EntityID) -> list[DataSource]:
        return [item for item in self.items.values() if item.project_id == project_id]

    async def count_by_project_ids(
        self, project_ids: tuple[EntityID, ...],
    ) -> dict[EntityID, int]:
        return {
            project_id: sum(item.project_id == project_id for item in self.items.values())
            for project_id in project_ids
        }

    async def save(self, entity: DataSource) -> DataSource:
        self.items[entity.id] = entity
        return entity

    async def delete(self, entity_id: EntityID) -> bool:
        return self.items.pop(entity_id, None) is not None


class InMemoryProjects(IProjectRepository):
    """Lưu Project trong bộ nhớ."""

    def __init__(self, project: Project) -> None:
        self.items = {project.id: project}

    async def get_by_id(self, entity_id: EntityID) -> Project | None:
        return self.items.get(entity_id)

    async def list_accessible_by_user(self, user_id: EntityID) -> list[Project]:
        return [item for item in self.items.values() if item.user_id == user_id]

    async def save(self, entity: Project) -> Project:
        self.items[entity.id] = entity
        return entity

    async def delete(self, entity_id: EntityID) -> bool:
        return self.items.pop(entity_id, None) is not None


class InMemoryMembers(IProjectMemberRepository):
    """Lưu membership trong bộ nhớ."""

    def __init__(self, members: list[ProjectMember] | None = None) -> None:
        self.items = {item.id: item for item in members or []}

    async def get_by_id(self, entity_id: EntityID) -> ProjectMember | None:
        return self.items.get(entity_id)

    async def list_by_project(self, project_id: EntityID) -> list[ProjectMember]:
        return [item for item in self.items.values() if item.project_id == project_id]

    async def get_by_project_and_user(
        self, project_id: EntityID, user_id: EntityID,
    ) -> ProjectMember | None:
        return next((item for item in self.items.values()
                     if item.project_id == project_id and item.user_id == user_id), None)

    async def save(self, entity: ProjectMember) -> ProjectMember:
        self.items[entity.id] = entity
        return entity

    async def delete(self, entity_id: EntityID) -> bool:
        return self.items.pop(entity_id, None) is not None


class InMemoryFiles:
    """Storage port trong bộ nhớ."""

    def __init__(self) -> None:
        self.items: dict[str, bytes] = {}

    async def save_file(self, project_id: str, filename: str, content: bytes) -> str:
        path = f"virtual/{project_id}/{filename}"
        self.items[path] = content
        return path

    async def read_file(self, file_path: str) -> bytes:
        return self.items[file_path]

    async def delete_file(self, file_path: str) -> None:
        self.items.pop(file_path, None)

    async def cleanup_empty_dir(self, project_id: str) -> None:
        del project_id


class RecordingUnitOfWork(IUnitOfWork):
    """Ghi nhận transaction boundaries."""

    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1
