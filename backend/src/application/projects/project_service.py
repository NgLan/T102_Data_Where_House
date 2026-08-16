"""Application service duy nhất cho module Project."""

from dataclasses import dataclass

from src.application.common.unit_of_work import IUnitOfWork
from src.application.projects.i_project_artifact_store import IProjectArtifactStore
from src.application.projects.i_project_service import IProjectService
from src.application.projects.input import (
    CreateProjectInput,
    ListProjectsInput,
    ProjectIdInput,
    UpdateProjectInput,
)
from src.application.projects.output import ProjectOutput, ProjectSummaryOutput
from src.common.exceptions.base import AppException
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_source.repository import IDataSourceRepository
from src.domain.project.entities import Project, ProjectMember
from src.domain.project.enums import ProjectRole
from src.domain.project.repository import IProjectMemberRepository, IProjectRepository
from src.domain.project.value_objects import ProjectDetails
from src.domain.shared.types import EntityID
from typing_extensions import override


@dataclass(frozen=True)
class ProjectServiceDependencies:
    """Outbound dependencies của Project service."""

    projects: IProjectRepository
    members: IProjectMemberRepository
    data_sources: IDataSourceRepository
    artifacts: IProjectArtifactStore
    unit_of_work: IUnitOfWork


class ProjectService(IProjectService):
    """Điều phối Project aggregate, authorization và transaction."""

    def __init__(self, dependencies: ProjectServiceDependencies, actor_id: EntityID) -> None:
        self._deps = dependencies
        self._actor_id = actor_id

    @override
    async def create_project(self, data: CreateProjectInput) -> ProjectOutput:
        """Tạo Project và OWNER membership trong một transaction."""
        try:
            project = _create_project(_create_details(data), self._actor_id)
            saved = await self._deps.projects.save(project)
            await self._deps.members.save(saved.create_owner_member())
            await self._deps.unit_of_work.commit()
            return ProjectOutput.from_domain(saved, ())
        except AppException:
            await self._deps.unit_of_work.rollback()
            raise

    @override
    async def list_projects(
        self,
        data: ListProjectsInput,
    ) -> tuple[ProjectSummaryOutput, ...]:
        """Liệt kê Project và aggregate source count trong hai truy vấn."""
        del data
        projects = await self._deps.projects.list_accessible_by_user(self._actor_id)
        project_ids = tuple(project.id for project in projects)
        counts = await self._deps.data_sources.count_by_project_ids(project_ids)
        return tuple(ProjectSummaryOutput.from_domain(project, counts.get(project.id, 0)) for project in projects)

    @override
    async def get_project(self, data: ProjectIdInput) -> ProjectOutput:
        """Lấy Project sau khi xác minh membership."""
        project = await self._get_accessible_project(data.project_id)
        sources = await self._deps.data_sources.list_by_project(project.id)
        return ProjectOutput.from_domain(project, tuple(sources))

    @override
    async def update_project(self, data: UpdateProjectInput) -> ProjectOutput:
        """Cập nhật thông tin Project ACTIVE nếu actor là OWNER."""
        try:
            project = await self._get_owned_project(data.project_id)
            project.update_info(_update_details(data))
            saved = await self._deps.projects.save(project)
            sources = await self._deps.data_sources.list_by_project(saved.id)
            await self._deps.unit_of_work.commit()
            return ProjectOutput.from_domain(saved, tuple(sources))
        except AppException:
            await self._deps.unit_of_work.rollback()
            raise

    @override
    async def delete_project(self, data: ProjectIdInput) -> None:
        """Xóa Project và artifact nếu actor là OWNER."""
        try:
            project = await self._get_owned_project(data.project_id)
            await self._deps.projects.delete(project.id)
            await self._deps.artifacts.delete_project_directory(project.id)
            await self._deps.unit_of_work.commit()
        except AppException:
            await self._deps.unit_of_work.rollback()
            raise

    async def _get_accessible_project(self, project_id: EntityID) -> Project:
        project = await self._get_project(project_id)
        if project.user_id == self._actor_id:
            return project
        membership = await self._membership(project.id)
        if membership is None:
            _raise_permission_denied()
        return project

    async def _get_owned_project(self, project_id: EntityID) -> Project:
        project = await self._get_project(project_id)
        if project.user_id == self._actor_id:
            return project
        membership = await self._membership(project.id)
        if membership is None or membership.role != ProjectRole.OWNER:
            _raise_permission_denied()
        return project

    async def _membership(self, project_id: EntityID) -> ProjectMember | None:
        return await self._deps.members.get_by_project_and_user(
            project_id,
            self._actor_id,
        )

    async def _get_project(self, project_id: EntityID) -> Project:
        project = await self._deps.projects.get_by_id(project_id)
        if project is None:
            raise BusinessException(
                code=ErrorCode.PROJECT_NOT_FOUND,
                message="Dự án không tồn tại.",
            )
        return project


def _create_details(data: CreateProjectInput) -> ProjectDetails:
    return ProjectDetails(data.name, data.requirement, data.domain, data.description)


def _update_details(data: UpdateProjectInput) -> ProjectDetails:
    return ProjectDetails(data.name, data.requirement, data.domain, data.description)


def _create_project(details: ProjectDetails, actor_id: EntityID) -> Project:
    return Project(
        name=details.name,
        requirement=details.requirement,
        user_id=actor_id,
        domain=details.domain,
        description=details.description,
    )


def _raise_permission_denied() -> None:
    raise BusinessException(
        code=ErrorCode.PERMISSION_DENIED,
        message="Bạn không có quyền thực hiện thao tác trên dự án này.",
    )
