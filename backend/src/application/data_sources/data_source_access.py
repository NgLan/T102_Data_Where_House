"""Authorization policy dùng chung cho Data Source service."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project.entities import Project
from src.domain.project.enums import ProjectRole
from src.domain.project.repository import IProjectMemberRepository, IProjectRepository
from src.domain.shared.types import EntityID


class DataSourceAccess:
    """Xác minh quyền đọc hoặc quyền OWNER trên một dự án."""

    def __init__(
        self,
        projects: IProjectRepository,
        members: IProjectMemberRepository,
        actor_id: EntityID,
    ) -> None:
        self._projects = projects
        self._members = members
        self._actor_id = actor_id

    async def require_member(self, project_id: EntityID) -> bool:
        """Xác minh membership và trả về quyền chỉnh sửa của actor."""
        project = await self._get_project(project_id)
        if project.user_id == self._actor_id:
            return True
        membership = await self._members.get_by_project_and_user(project_id, self._actor_id)
        if membership is None:
            _raise_permission_denied()
        return membership.role == ProjectRole.OWNER

    async def require_owner(self, project_id: EntityID) -> Project:
        """Chỉ cho phép owner gốc hoặc membership OWNER."""
        project = await self._get_project(project_id)
        if project.user_id == self._actor_id:
            return project
        membership = await self._members.get_by_project_and_user(project_id, self._actor_id)
        if membership is None or membership.role != ProjectRole.OWNER:
            _raise_permission_denied()
        return project

    async def _get_project(self, project_id: EntityID) -> Project:
        project = await self._projects.get_by_id(project_id)
        if project is None:
            raise BusinessException(
                code=ErrorCode.PROJECT_NOT_FOUND,
                message="Dự án không tồn tại.",
            )
        return project


def _raise_permission_denied() -> None:
    raise BusinessException(
        code=ErrorCode.PERMISSION_DENIED,
        message="Bạn không có quyền thao tác trên nguồn dữ liệu của dự án này.",
    )
