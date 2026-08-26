"""Application service chứa trọn các use case của Data Source module."""

from src.application.common.file_mutation_log import FileMutationLog
from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_sources.constraint_mapper import map_constraints
from src.application.data_sources.data_source_upload_workflow import DataSourceUploadWorkflow
from src.application.data_sources.i_data_source_service import (
    IDataSourceFileStore,
    IDataSourceService,
)
from src.application.data_sources.input import (
    DataSourceIdInput,
    DataSourcePreviewInput,
    ListDataSourcesInput,
    UpdateDataSourceColumnInput,
    UploadDataSourcesInput,
)
from src.application.data_sources.output import (
    DataSourceListOutput,
    DataSourceOutput,
    PreviewOutput,
    UploadDataSourcesOutput,
)
from src.application.data_sources.source_analysis_ports import ISourceFileInspector
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_source.entities import DataSource
from src.domain.data_source.i_data_source_repository import IDataSourceRepository
from src.domain.data_source.value_objects import ColumnUpdate
from src.domain.project.i_project_repository import IProjectRepository
from typing_extensions import override


class DataSourceService(IDataSourceService):
    """Điều phối source storage, authorization và transaction."""

    def __init__(
        self,
        sources: IDataSourceRepository,
        files: IDataSourceFileStore,
        inspector: ISourceFileInspector,
        unit_of_work: IUnitOfWork,
        access: ProjectAccessPolicy,
        projects: IProjectRepository,
    ) -> None:
        self._sources = sources
        self._files = files
        self._inspector = inspector
        self._unit_of_work = unit_of_work
        self._access = access
        self._projects = projects
        self._upload_workflow = DataSourceUploadWorkflow(
            sources, files, inspector, unit_of_work, access, projects
        )

    @override
    async def list_data_sources(self, data: ListDataSourcesInput) -> DataSourceListOutput:
        """Liệt kê nguồn nếu actor là thành viên dự án."""
        access = await self._access.require_member(data.project_id)
        sources = await self._sources.list_by_project(data.project_id)
        return DataSourceListOutput(
            items=tuple(DataSourceOutput.from_domain(source) for source in sources),
            can_edit=access.can_edit,
        )

    @override
    async def upload_data_sources(self, data: UploadDataSourcesInput) -> UploadDataSourcesOutput:
        """Upload batch CSV nếu actor là OWNER."""
        return await self._upload_workflow.execute(data)

    @override
    async def get_preview(self, data: DataSourcePreviewInput) -> PreviewOutput:
        """Đọc preview table được chọn nếu actor là thành viên dự án."""
        await self._access.require_member(data.project_id)
        source = await self._get_source(data)
        content = await self._files.read_file(source.location)
        return self._inspector.preview(content, source.name, data.table_name)

    @override
    async def update_column(self, data: UpdateDataSourceColumnInput) -> DataSourceOutput:
        """Cập nhật metadata cột nếu actor là OWNER."""
        target = data.target
        async with self._unit_of_work:
            project = await self._access.require_owner(target.project_id)
            source = await self._get_source(DataSourceIdInput(target.project_id, target.data_source_id))
            previous_schema = source.schema_metadata
            update = ColumnUpdate(
                target.table_name,
                target.column_name,
                data.data_type,
                data.distinct_values,
                map_constraints(data.constraints),
            )
            if not source.update_column(update):
                raise BusinessException(
                    code=ErrorCode.DATA_SOURCE_COLUMN_NOT_FOUND,
                    message="Không tìm thấy cột trong nguồn dữ liệu.",
                )
            saved = await self._sources.save(source)
            if saved.schema_metadata != previous_schema:
                project.increment_source_revision()
                await self._projects.save(project)
            await self._unit_of_work.commit()
        return DataSourceOutput.from_domain(saved)

    @override
    async def delete_data_source(self, data: DataSourceIdInput) -> None:
        """Xóa source và file vật lý nếu actor là OWNER."""
        mutations = FileMutationLog(self._files)
        try:
            async with self._unit_of_work:
                project = await self._access.require_owner(data.project_id)
                source = await self._get_source(data)
                await mutations.remove(str(data.project_id), source.name, source.location)
                await self._sources.delete(source.id)
                project.increment_source_revision()
                await self._projects.save(project)
                await self._unit_of_work.commit()
        except Exception:
            await mutations.rollback()
            raise
        await self._files.cleanup_empty_dir(str(data.project_id))

    async def _get_source(self, data: DataSourceIdInput) -> DataSource:
        source = await self._sources.get_by_id(data.data_source_id)
        if source is None or source.project_id != data.project_id:
            raise BusinessException(
                code=ErrorCode.DATA_SOURCE_NOT_FOUND,
                message="Nguồn dữ liệu không tồn tại trong dự án.",
            )
        return source
