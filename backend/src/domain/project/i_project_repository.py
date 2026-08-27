"""Giao diện repository cho Project."""

from abc import abstractmethod
from datetime import datetime

from src.domain.project.entities import Project
from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.shared.types import EntityID


class IProjectRepository(IBaseRepository[Project]):
    """Định nghĩa các truy vấn persistence dành cho Project."""

    @abstractmethod
    async def list_accessible_by_user(self, user_id: EntityID) -> list[Project]:
        """Lấy các dự án người dùng được phép truy cập.

        Args:
            user_id: Định danh người dùng cần kiểm tra quyền.

        Returns:
            Danh sách dự án có thể truy cập.
        """

    @abstractmethod
    async def get_latest_activity_by_project_ids(
        self,
        project_ids: tuple[EntityID, ...],
    ) -> dict[EntityID, datetime]:
        """Lấy mốc thời gian hoạt động gần nhất theo từng dự án qua tất cả các module.

        Args:
            project_ids: Danh sách ID các dự án.

        Returns:
            Ánh xạ từ project_id sang thời điểm hoạt động mới nhất.
        """

    async def get_by_id_for_update(self, entity_id: EntityID) -> Project | None:
        """Lấy Project và khóa row cho mutation revision."""
        return await self.get_by_id(entity_id)
