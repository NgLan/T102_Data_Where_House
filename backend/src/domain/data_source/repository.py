"""Giao diện Repository cho miền Nguồn dữ liệu (Data Source)."""

from abc import abstractmethod

from src.domain.data_source.entities import DataSource
from src.domain.shared.repository import IBaseRepository
from src.domain.shared.types import EntityID


class IDataSourceRepository(IBaseRepository[DataSource]):
    """Interface trừu tượng cho thao tác lưu trữ thực thể DataSource."""

    @abstractmethod
    async def list_by_project(self, project_id: EntityID) -> list[DataSource]:
        """Lấy danh sách nguồn dữ liệu thuộc một dự án."""
        pass

    @abstractmethod
    async def count_by_project_ids(
        self,
        project_ids: tuple[EntityID, ...],
    ) -> dict[EntityID, int]:
        """Đếm nguồn dữ liệu theo Project mà không tải entity."""
        pass
