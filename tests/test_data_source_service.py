"""Tests cho Data Source application service thống nhất."""

from uuid import uuid4

import pytest
from src.application.data_sources.data_source_service import (
    DataSourceService,
    DataSourceServiceDependencies,
)
from src.application.data_sources.input import (
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
from src.infrastructure.storage.file_parser_service_impl import FileParserServiceImpl

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
    dependencies = DataSourceServiceDependencies(
        projects=InMemoryProjects(project), members=InMemoryMembers(members),
        sources=InMemoryDataSources(), files=InMemoryFiles(),
        parser=FileParserServiceImpl(), unit_of_work=RecordingUnitOfWork(),
    )
    service_actor = owner_id if member_role is None else actor_id
    return DataSourceService(dependencies, service_actor), dependencies, project


@pytest.mark.asyncio
async def test_owner_data_source_lifecycle() -> None:
    """OWNER upload, list, preview, sửa schema và xóa source."""
    service, dependencies, project = create_service(uuid4())
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

    updated = await service.update_column(UpdateDataSourceColumnInput(
        project.id, source.id, "orders", "status", "OPTION", ("new", "done"),
    ))
    assert updated.tables[0].columns[1].options == ("new", "done")

    await service.delete_data_source(DataSourceIdInput(project.id, source.id))
    assert await dependencies.sources.get_by_id(source.id) is None
    assert dependencies.unit_of_work.commits == 3


@pytest.mark.asyncio
async def test_member_is_read_only() -> None:
    """MEMBER được đọc nhưng mọi mutation bị từ chối."""
    actor_id = uuid4()
    service, _, project = create_service(actor_id, ProjectRole.MEMBER)
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
    service, _, project = create_service(uuid4())
    command = UploadDataSourcesInput(project.id, (UploadFileInput("orders.csv", CSV_CONTENT),))
    first = await service.upload_data_sources(command)
    second = await service.upload_data_sources(command)
    assert first.data_sources[0].id == second.data_sources[0].id

    with pytest.raises(BusinessException) as raised:
        await service.upload_data_sources(UploadDataSourcesInput(
            project.id, (UploadFileInput("orders.xlsx", b"invalid"),),
        ))
    assert raised.value.code == ErrorCode.INVALID_FILE_FORMAT
