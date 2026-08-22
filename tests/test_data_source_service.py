"""Tests cho Data Source application service thống nhất."""

from uuid import uuid4

import pytest
from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.data_sources.data_source_service import (
    DataSourceService,
)
from src.application.data_sources.input import (
    CheckConstraintInput,
    DataSourceColumnTargetInput,
    DataSourceIdInput,
    ListDataSourcesInput,
    UpdateDataSourceColumnInput,
    UploadDataSourcesInput,
    UploadFileInput,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project.entities import Project, ProjectMember
from src.domain.project.enums import ProjectRole
from src.infrastructure.storage.csv_parser import CsvParser

from tests.data_source_fakes import (
    InMemoryDataSources,
    InMemoryFiles,
    InMemoryMembers,
    InMemoryProjects,
    RecordingUnitOfWork,
)

CSV_CONTENT = b"id,status,amount\n1,new,10\n2,done,20\n"


def create_service(actor_id, member_role: ProjectRole | None = None):
    """Tạo service và dependencies cho một actor."""
    owner_id = uuid4()
    project = Project(name="Test project", requirement="A valid requirement", user_id=owner_id)
    members = []
    if member_role:
        members.append(ProjectMember(project_id=project.id, user_id=actor_id, role=member_role))
    service_actor = owner_id if member_role is None else actor_id
    projects = InMemoryProjects(project)
    member_repository = InMemoryMembers(members)
    sources = InMemoryDataSources()
    unit_of_work = RecordingUnitOfWork()
    service = DataSourceService(
        sources=sources,
        files=InMemoryFiles(),
        csv_parser=CsvParser(),
        unit_of_work=unit_of_work,
        access=ProjectAccessPolicy(projects, member_repository, service_actor),
        projects=projects,
    )
    return service, sources, unit_of_work, project
@pytest.mark.asyncio
async def test_owner_data_source_lifecycle() -> None:
    """OWNER upload, list, preview, sửa schema và xóa source."""
    service, sources, unit_of_work, project = create_service(uuid4())
    uploaded = await service.upload_data_sources(UploadDataSourcesInput(
        project.id, (UploadFileInput("orders.csv", CSV_CONTENT),),
    ))
    source = uploaded.data_sources[0]
    listed = await service.list_data_sources(ListDataSourcesInput(project.id))
    preview = await service.get_preview(DataSourceIdInput(project.id, source.id))

    assert listed.can_edit is True
    assert listed.items == (source,)
    assert preview.total_rows == 2
    assert preview.rows[0]["status"] == "new"

    updated = await service.update_column(
        UpdateDataSourceColumnInput(
            target=DataSourceColumnTargetInput(
                project.id,
                source.id,
                "orders",
                "status",
            ),
            data_type="CATEGORY",
            distinct_values=("new", "done"),
            constraints=(CheckConstraintInput("status <> ''"),),
        )
    )
    updated_column = updated.tables[0].columns[1]
    assert updated_column.data_type == "CATEGORY"
    assert updated_column.distinct_values == ("new", "done")
    assert updated_column.constraints[0].expression == "status <> ''"

    await service.delete_data_source(DataSourceIdInput(project.id, source.id))
    assert await sources.get_by_id(source.id) is None
    assert unit_of_work.commits == 3
    assert project.source_revision == 3


@pytest.mark.asyncio
async def test_member_is_read_only() -> None:
    """MEMBER được đọc nhưng mọi mutation bị từ chối."""
    actor_id = uuid4()
    service, _, _, project = create_service(actor_id, ProjectRole.MEMBER)
    listed = await service.list_data_sources(ListDataSourcesInput(project.id))
    assert listed.can_edit is False

    with pytest.raises(BusinessException) as raised:
        await service.upload_data_sources(UploadDataSourcesInput(
            project.id, (UploadFileInput("orders.csv", CSV_CONTENT),),
        ))
    assert raised.value.code == ErrorCode.PERMISSION_DENIED


@pytest.mark.asyncio
async def test_upload_upserts_same_filename_and_validates_batch() -> None:
    """Cùng tên giữ nguyên ID; file sai định dạng bị chặn trước storage."""
    service, _, _, project = create_service(uuid4())
    command = UploadDataSourcesInput(project.id, (UploadFileInput("orders.csv", CSV_CONTENT),))
    first = await service.upload_data_sources(command)
    second = await service.upload_data_sources(command)
    assert first.data_sources[0].id == second.data_sources[0].id

    with pytest.raises(BusinessException) as raised:
        await service.upload_data_sources(UploadDataSourcesInput(
            project.id, (UploadFileInput("orders.xlsx", b"invalid"),),
        ))
    assert raised.value.code == ErrorCode.INVALID_FILE_FORMAT
