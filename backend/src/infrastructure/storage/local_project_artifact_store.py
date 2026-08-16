"""Local storage adapter cho Project artifact port."""

from src.application.projects.i_project_artifact_store import IProjectArtifactStore
from src.domain.shared.types import EntityID
from src.infrastructure.storage.file_storage import IFileStorage
from typing_extensions import override


class LocalProjectArtifactStore(IProjectArtifactStore):
    """Điều chỉnh IFileStorage hiện có về contract tối thiểu của Project."""

    def __init__(self, storage: IFileStorage) -> None:
        """Khởi tạo adapter với local file storage."""
        self._storage = storage

    @override
    async def delete_file(self, file_path: str) -> None:
        """Xóa một artifact nếu tồn tại."""
        await self._storage.delete_file(file_path)

    @override
    async def delete_project_directory(self, project_id: EntityID) -> None:
        """Xóa toàn bộ thư mục artifact của Project."""
        await self._storage.delete_directory(str(project_id))
