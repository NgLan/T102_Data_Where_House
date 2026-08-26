"""Giao diện repository cho ProjectSession."""

from abc import abstractmethod

from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.enums import SessionPurpose
from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.shared.types import EntityID


class IProjectSessionRepository(IBaseRepository[ProjectSession]):
    @abstractmethod
    async def get_by_id_for_update(self, entity_id: EntityID) -> ProjectSession | None:
        """Load a session with a row lock for turn acquisition."""

    """Định nghĩa persistence dành cho phiên làm việc dự án."""

    @abstractmethod
    async def list_by_project(self, project_id: EntityID) -> list[ProjectSession]:
        """Lấy danh sách phiên làm việc của dự án.

        Args:
            project_id: Định danh dự án.

        Returns:
            Danh sách phiên làm việc của dự án.
        """

    @abstractmethod
    async def list_by_project_user(self, project_id: EntityID, user_id: EntityID) -> list[ProjectSession]:
        """Lấy các session của một người dùng trong project."""

    @abstractmethod
    async def list_by_project_user_and_purpose(
        self,
        project_id: EntityID,
        user_id: EntityID,
        purpose: SessionPurpose,
    ) -> list[ProjectSession]:
        """Lấy session của actor theo đúng mục đích nghiệp vụ."""

    @abstractmethod
    async def get_active_by_project_purpose_for_update(
        self,
        project_id: EntityID,
        purpose: SessionPurpose,
    ) -> ProjectSession | None:
        """Lấy active session theo purpose bằng row lock."""
