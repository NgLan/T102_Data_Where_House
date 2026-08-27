"""Application service duy nhất cho module Project."""

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.projects.i_project_service import IProjectArtifactStore, IProjectService
from src.application.projects.input import (
    CreateProjectInput,
    ProjectIdInput,
    SaveRawRequirementInput,
    UpdateProjectInput,
)
from src.application.projects.output import (
    ProjectOutput,
    ProjectSummaryOutput,
    RawRequirementOutput,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.entities import DataModel
from src.domain.data_model.i_data_model_repository import IDataModelRepository
from src.domain.data_source.i_data_source_repository import IDataSourceRepository
from src.domain.project.entities import Project
from src.domain.project.i_project_member_repository import IProjectMemberRepository
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.project.value_objects import ProjectDetails
from src.domain.requirement.i_requirement_repository import IRequirementRepository
from typing_extensions import override


class ProjectService(IProjectService):
    """Điều phối Project aggregate, authorization và transaction."""

    def __init__(
        self,
        projects: IProjectRepository,
        members: IProjectMemberRepository,
        data_sources: IDataSourceRepository,
        requirements: IRequirementRepository,
        data_models: IDataModelRepository,
        artifacts: IProjectArtifactStore,
        unit_of_work: IUnitOfWork,
        access: ProjectAccessPolicy,
    ) -> None:
        self._projects = projects
        self._members = members
        self._data_sources = data_sources
        self._requirements = requirements
        self._data_models = data_models
        self._artifacts = artifacts
        self._unit_of_work = unit_of_work
        self._access = access

    @override
    async def create_project(self, data: CreateProjectInput) -> ProjectOutput:
        """Tạo Project và OWNER membership trong một transaction."""
        async with self._unit_of_work:
            details = _project_details(data)
            project = Project(
                name=details.name,
                requirement=details.requirement,
                user_id=self._access.actor_id,
                domain=details.domain,
                description=details.description,
            )
            saved = await self._projects.save(project)
            await self._members.save(saved.create_owner_member())
            await self._unit_of_work.commit()
        return ProjectOutput.from_domain(saved, (), ())

    @override
    async def list_projects(self) -> tuple[ProjectSummaryOutput, ...]:
        """Liệt kê Project actor hiện tại được truy cập, sắp xếp theo hoạt động gần nhất."""
        projects = await self._projects.list_accessible_by_user(self._access.actor_id)
        project_ids = tuple(project.id for project in projects)
        counts = await self._data_sources.count_by_project_ids(project_ids)
        data_models = await self._data_models.list_by_project_ids(project_ids)
        activities = await self._projects.get_latest_activity_by_project_ids(project_ids)
        summaries = [
            ProjectSummaryOutput.from_domain(
                project,
                counts.get(project.id, 0),
                _is_data_model_outdated(project, data_models.get(project.id)),
                activities.get(project.id, project.updated_at),
            )
            for project in projects
        ]
        summaries.sort(key=lambda item: item.updated_at, reverse=True)
        return tuple(summaries)

    @override
    async def get_project(self, data: ProjectIdInput) -> ProjectOutput:
        """Lấy Project sau khi xác minh membership."""
        access = await self._access.require_member(data.project_id)
        sources = await self._data_sources.list_by_project(access.project.id)
        requirements = await self._requirements.list_by_project(access.project.id)
        return ProjectOutput.from_domain(access.project, tuple(sources), tuple(requirements))

    @override
    async def update_project(self, data: UpdateProjectInput) -> ProjectOutput:
        """Cập nhật Project nếu actor là OWNER."""
        async with self._unit_of_work:
            project = await self._access.require_owner(data.project_id)
            project.update_info(
                ProjectDetails(data.name, project.requirement, data.domain, data.description)
            )
            saved = await self._projects.save(project)
            await self._unit_of_work.commit()
        sources = await self._data_sources.list_by_project(saved.id)
        requirements = await self._requirements.list_by_project(saved.id)
        return ProjectOutput.from_domain(saved, tuple(sources), tuple(requirements))

    @override
    async def save_raw_requirement(
        self, data: SaveRawRequirementInput
    ) -> RawRequirementOutput:
        """Lưu riêng Raw Requirement bằng row lock và expected revision."""
        async with self._unit_of_work:
            project = await self._access.require_owner_for_update(data.project_id)
            if project.requirement_revision != data.expected_revision:
                raise BusinessException(
                    ErrorCode.REQUIREMENT_REVISION_CONFLICT,
                    "Requirement đã thay đổi; hãy tải lại revision mới nhất.",
                )
            project.save_requirement(data.requirement)
            saved = await self._projects.save(project)
            await self._unit_of_work.commit()
        return RawRequirementOutput(saved.requirement, saved.requirement_revision)

    @override
    async def delete_project(self, data: ProjectIdInput) -> None:
        """Xóa Project và artifact nếu actor là OWNER."""
        async with self._unit_of_work:
            project = await self._access.require_owner(data.project_id)
            await self._projects.delete(project.id)
            await self._artifacts.delete_project_directory(project.id)
            await self._unit_of_work.commit()


def _project_details(data: CreateProjectInput) -> ProjectDetails:
    return ProjectDetails(data.name, data.requirement, data.domain, data.description)


def _is_data_model_outdated(project: Project, data_model: DataModel | None) -> bool:
    """Chỉ coi Data Model hiện hữu và lệch analysis revision là outdated."""
    if data_model is None:
        return False
    return data_model.is_outdated(
        project.analyzed_requirement_revision,
        project.analyzed_source_revision,
    )
