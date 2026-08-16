"""Kiểm thử hành vi Project application service và default user."""

from uuid import UUID, uuid4

import pytest
from src.application.projects.input import (
    CreateProjectInput,
    ListProjectsInput,
    ProjectIdInput,
    UpdateProjectInput,
)
from src.application.projects.project_service import ProjectService, ProjectServiceDependencies
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import DataSourceType
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata, TableMetadata
from src.domain.project.entities import ProjectMember
from src.domain.project.enums import ProjectRole
from src.domain.user.entities import User
from src.infrastructure.database.constants import DEFAULT_USER_EMAIL, DEFAULT_USER_ID, DEFAULT_USER_NAME

from tests.project_fakes import (
    InMemoryDataSourceRepository,
    InMemoryProjectMemberRepository,
    InMemoryProjectRepository,
    RecordingArtifactStore,
    RecordingUnitOfWork,
)


def build_service(actor_id: UUID = DEFAULT_USER_ID):
    """Tạo service và adapter quan sát được cho mỗi test."""
    dependencies = ProjectServiceDependencies(
        InMemoryProjectRepository(),
        InMemoryProjectMemberRepository(),
        InMemoryDataSourceRepository(),
        RecordingArtifactStore(),
        RecordingUnitOfWork(),
    )
    return ProjectService(dependencies, actor_id), dependencies


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
    members = await deps.members.list_by_project(result.id)
    assert (result.name, result.domain) == ("Sales Analytics", "retail")
    assert result.data_source_count == 0
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
    await deps.members.save(ProjectMember(project_id=created.id, user_id=member_id))
    deps.projects.accessible.add((created.id, member_id))
    member_service = ProjectService(deps, member_id)
    assert len(await member_service.list_projects(ListProjectsInput())) == 1
    assert (await member_service.get_project(ProjectIdInput(created.id))).id == created.id
    with pytest.raises(BusinessException) as error:
        await member_service.update_project(
            UpdateProjectInput(
                created.id,
                "Other name",
                "Một yêu cầu hợp lệ",
            )
        )
    assert error.value.code == ErrorCode.PERMISSION_DENIED
    with pytest.raises(BusinessException) as delete_error:
        await member_service.delete_project(ProjectIdInput(created.id))
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
    outsider = ProjectService(deps, uuid4())
    with pytest.raises(BusinessException) as forbidden:
        await outsider.get_project(ProjectIdInput(created.id))
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
            project_id=created.id,
            name="orders.csv",
            location="project/orders.csv",
            type=DataSourceType.CSV,
        )
    )
    updated = await service.update_project(
        UpdateProjectInput(
            created.id,
            "Updated sales project",
            "Theo dõi doanh thu hằng ngày",
        )
    )
    assert updated.data_source_count == 1
    assert updated.data_sources[0].id == source.id
    assert await deps.data_sources.get_by_id(source.id) == source
    assert deps.artifacts.files == []


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
            project_id=created.id,
            name="orders.csv",
            location="project/orders.csv",
            type=DataSourceType.CSV,
        )
    )
    summaries = await service.list_projects(ListProjectsInput())
    assert summaries[0].data_source_count == 1


@pytest.mark.asyncio
async def test_project_output_reuses_data_source_schema_value_objects() -> None:
    """Application output giữ nguyên immutable Domain schema metadata."""
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
            project_id=created.id,
            name="orders.csv",
            location="project/orders.csv",
            type=DataSourceType.CSV,
            schema_metadata=schema,
        )
    )
    output = await service.get_project(ProjectIdInput(created.id))
    assert output.data_sources[0].schema_metadata is schema
    assert output.data_sources[0].tables is schema.tables


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
    await service.delete_project(ProjectIdInput(created.id))
    assert await deps.projects.get_by_id(created.id) is None
    assert deps.artifacts.projects == [created.id]
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
    dependencies = ProjectServiceDependencies(
        InMemoryProjectRepository(),
        FailingMemberRepository(),
        InMemoryDataSourceRepository(),
        RecordingArtifactStore(),
        unit_of_work,
    )
    service = ProjectService(dependencies, DEFAULT_USER_ID)
    with pytest.raises(InfrastructureException):
        await service.create_project(
            CreateProjectInput(
                name="Sales project",
                requirement="Theo dõi doanh thu",
            )
        )
    assert (unit_of_work.commits, unit_of_work.rollbacks) == (0, 1)
