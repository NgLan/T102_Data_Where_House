"""Kiểm thử hành vi Project application service và default user."""

from dataclasses import dataclass, replace
from uuid import UUID, uuid4

import pytest
from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.projects.input import (
    CreateProjectInput,
    ProjectIdInput,
    UpdateProjectInput,
)
from src.application.projects.project_service import ProjectService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import DataSourceType
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata, TableMetadata
from src.domain.project.entities import ProjectMember
from src.domain.project.enums import ProjectRole
from src.domain.requirement.entities import Requirement
from src.domain.user.entities import User

from tests.project_fakes import (
    InMemoryDataSourceRepository,
    InMemoryProjectMemberRepository,
    InMemoryProjectRepository,
    InMemoryRequirementRepository,
    RecordingArtifactStore,
    RecordingUnitOfWork,
)

DEFAULT_USER_ID = UUID("a678ac27-3077-5ef2-8919-5218b2e48791")
DEFAULT_USER_NAME = "annv"
DEFAULT_USER_EMAIL = "an.nguyen@dataworks.vn"


@dataclass(frozen=True)
class ProjectTestDependencies:
    projects: InMemoryProjectRepository
    members: InMemoryProjectMemberRepository
    data_sources: InMemoryDataSourceRepository
    requirements: InMemoryRequirementRepository
    artifacts: RecordingArtifactStore
    unit_of_work: RecordingUnitOfWork
    access: ProjectAccessPolicy


def _service(dependencies: ProjectTestDependencies) -> ProjectService:
    return ProjectService(
        projects=dependencies.projects,
        members=dependencies.members,
        data_sources=dependencies.data_sources,
        requirements=dependencies.requirements,
        artifacts=dependencies.artifacts,
        unit_of_work=dependencies.unit_of_work,
        access=dependencies.access,
    )


def build_service(actor_id: UUID = DEFAULT_USER_ID):
    """Tạo service và adapter quan sát được cho mỗi test."""
    projects = InMemoryProjectRepository()
    members = InMemoryProjectMemberRepository()
    dependencies = ProjectTestDependencies(
        projects,
        members,
        InMemoryDataSourceRepository(),
        InMemoryRequirementRepository(),
        RecordingArtifactStore(),
        RecordingUnitOfWork(),
        ProjectAccessPolicy(projects, members, actor_id),
    )
    return _service(dependencies), dependencies


def service_for(dependencies: ProjectTestDependencies, actor_id: UUID) -> ProjectService:
    access = ProjectAccessPolicy(dependencies.projects, dependencies.members, actor_id)
    return _service(replace(dependencies, access=access))


@pytest.mark.asyncio
async def test_create_project_creates_owner_and_commits_once() -> None:
    """Create chuẩn hóa payload, tạo OWNER và chỉ commit một lần."""
    service, deps = build_service()
    result = await service.create_project(
        CreateProjectInput(
            name="  Sales   Analytics  ",
            requirement=" Theo dõi doanh thu theo ngày ",
            domain=" retail ",
        )
    )
    members = await deps.members.list_by_project(result.summary.id)
    assert (result.summary.name, result.summary.domain) == ("Sales Analytics", "retail")
    assert result.summary.data_source_count == 0
    assert members[0].role == ProjectRole.OWNER
    assert deps.unit_of_work.commits == 1


@pytest.mark.asyncio
async def test_member_can_list_and_get_but_cannot_update() -> None:
    """Member có quyền đọc, nhưng mutation vẫn thuộc OWNER."""
    owner_service, deps = build_service()
    created = await owner_service.create_project(
        CreateProjectInput(
            name="Sales project",
            requirement="Theo dõi doanh thu",
        )
    )
    member_id = uuid4()
    await deps.members.save(ProjectMember(project_id=created.summary.id, user_id=member_id))
    deps.projects.accessible.add((created.summary.id, member_id))
    member_service = service_for(deps, member_id)
    assert len(await member_service.list_projects()) == 1
    assert (
        await member_service.get_project(ProjectIdInput(created.summary.id))
    ).summary.id == created.summary.id
    with pytest.raises(BusinessException) as error:
        await member_service.update_project(
            UpdateProjectInput(
                created.summary.id,
                "Other name",
                "Một yêu cầu hợp lệ",
            )
        )
    assert error.value.code == ErrorCode.PERMISSION_DENIED
    with pytest.raises(BusinessException) as delete_error:
        await member_service.delete_project(ProjectIdInput(created.summary.id))
    assert delete_error.value.code == ErrorCode.PERMISSION_DENIED


@pytest.mark.asyncio
async def test_outsider_is_denied_and_missing_project_is_not_found() -> None:
    """Phân biệt authorization failure và resource không tồn tại."""
    owner_service, deps = build_service()
    created = await owner_service.create_project(
        CreateProjectInput(
            name="Sales project",
            requirement="Theo dõi doanh thu",
        )
    )
    outsider = service_for(deps, uuid4())
    with pytest.raises(BusinessException) as forbidden:
        await outsider.get_project(ProjectIdInput(created.summary.id))
    with pytest.raises(BusinessException) as missing:
        await outsider.get_project(ProjectIdInput(uuid4()))
    assert forbidden.value.code == ErrorCode.PERMISSION_DENIED
    assert missing.value.code == ErrorCode.PROJECT_NOT_FOUND


@pytest.mark.asyncio
async def test_update_project_does_not_mutate_data_sources() -> None:
    """Project PUT chỉ sửa Project; Data Source do use case riêng sở hữu."""
    service, deps = build_service()
    created = await service.create_project(
        CreateProjectInput(
            name="Sales project",
            requirement="Theo dõi doanh thu",
        )
    )
    source = await deps.data_sources.save(
        DataSource(
            project_id=created.summary.id,
            name="orders.csv",
            location="project/orders.csv",
            type=DataSourceType.CSV,
        )
    )
    updated = await service.update_project(
        UpdateProjectInput(
            created.summary.id,
            "Updated sales project",
            "Theo dõi doanh thu hằng ngày",
        )
    )
    assert updated.summary.data_source_count == 1
    assert updated.data_sources[0].id == source.id
    assert await deps.data_sources.get_by_id(source.id) == source


@pytest.mark.asyncio
async def test_list_projects_returns_source_count_without_loading_entities() -> None:
    """Project list trả aggregate count thay vì tải schema metadata."""
    service, deps = build_service()
    created = await service.create_project(
        CreateProjectInput(
            name="Sales project",
            requirement="Theo dõi doanh thu",
        )
    )
    await deps.data_sources.save(
        DataSource(
            project_id=created.summary.id,
            name="orders.csv",
            location="project/orders.csv",
            type=DataSourceType.CSV,
        )
    )
    summaries = await service.list_projects()
    assert summaries[0].data_source_count == 1


@pytest.mark.asyncio
async def test_project_output_reuses_data_source_application_output() -> None:
    """Project output tái sử dụng Data Source output độc lập Domain boundary."""
    service, deps = build_service()
    created = await service.create_project(
        CreateProjectInput(name="Sales project", requirement="Theo dõi doanh thu")
    )
    schema = SchemaMetadata(
        tables=(
            TableMetadata(
                name="orders",
                columns=(ColumnMetadata(name="id", data_type="NUMBER"),),
            ),
        )
    )
    await deps.data_sources.save(
        DataSource(
            project_id=created.summary.id,
            name="orders.csv",
            location="project/orders.csv",
            type=DataSourceType.CSV,
            schema_metadata=schema,
        )
    )
    output = await service.get_project(ProjectIdInput(created.summary.id))
    assert output.data_sources[0].tables[0].name == "orders"
    assert output.data_sources[0].tables[0].columns[0].data_type == "NUMBER"


@pytest.mark.asyncio
async def test_project_detail_includes_structured_requirements() -> None:
    """Project detail mang Requirement có cấu trúc nhưng summary không mang raw text."""
    service, deps = build_service()
    created = await service.create_project(CreateProjectInput(name="Sales project"))
    structured = await deps.requirements.save(
        Requirement(
            project_id=created.summary.id,
            title="Doanh thu theo tháng",
            description="Tổng hợp doanh thu theo tháng.",
        )
    )

    output = await service.get_project(ProjectIdInput(created.summary.id))

    assert output.requirement is None
    assert output.requirements[0].id == structured.id


@pytest.mark.asyncio
async def test_delete_project_removes_artifacts_after_owner_check() -> None:
    """Delete xóa aggregate và artifact rồi commit."""
    service, deps = build_service()
    created = await service.create_project(
        CreateProjectInput(
            name="Project to delete",
            requirement="Yêu cầu xóa dự án",
        )
    )
    await service.delete_project(ProjectIdInput(created.summary.id))
    assert await deps.projects.get_by_id(created.summary.id) is None
    assert deps.artifacts.projects == [created.summary.id]
    assert deps.unit_of_work.commits == 2


def test_default_user_entity() -> None:
    """Default user constants tạo được entity hợp lệ."""
    user = User(id=DEFAULT_USER_ID, username=DEFAULT_USER_NAME, email=DEFAULT_USER_EMAIL)
    assert str(user.id) == "a678ac27-3077-5ef2-8919-5218b2e48791"
    assert (user.username, user.email.value) == ("annv", "an.nguyen@dataworks.vn")


@pytest.mark.asyncio
async def test_create_rolls_back_when_member_persistence_fails() -> None:
    """Create rollback transaction nếu một bước sau Project save thất bại."""

    class FailingMemberRepository(InMemoryProjectMemberRepository):
        async def save(self, entity: ProjectMember) -> ProjectMember:
            raise InfrastructureException(ErrorCode.DATABASE_ERROR, "Database error.")

    unit_of_work = RecordingUnitOfWork()
    projects = InMemoryProjectRepository()
    members = FailingMemberRepository()
    dependencies = ProjectTestDependencies(
        projects,
        members,
        InMemoryDataSourceRepository(),
        InMemoryRequirementRepository(),
        RecordingArtifactStore(),
        unit_of_work,
        ProjectAccessPolicy(projects, members, DEFAULT_USER_ID),
    )
    service = _service(dependencies)
    with pytest.raises(InfrastructureException):
        await service.create_project(
            CreateProjectInput(
                name="Sales project",
                requirement="Theo dõi doanh thu",
            )
        )
    assert (unit_of_work.commits, unit_of_work.rollbacks) == (0, 1)
