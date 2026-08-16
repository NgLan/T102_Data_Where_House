"""Outbound port dọn dẹp artifact vật lý của Project."""

from abc import ABC, abstractmethod

from src.domain.shared.types import EntityID


class IProjectArtifactStore(ABC):
    """Hợp đồng storage tối thiểu mà Project application cần sử dụng."""

    @abstractmethod
    async def delete_file(self, file_path: str) -> None:
        """Xóa một artifact theo đường dẫn nội bộ."""
        pass

    @abstractmethod
    async def delete_project_directory(self, project_id: EntityID) -> None:
        """Xóa toàn bộ artifact vật lý của Project."""
        pass
