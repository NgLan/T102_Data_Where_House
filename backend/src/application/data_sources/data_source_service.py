"""Application service chứa trọn các use case của Data Source module."""

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_sources.constraint_mapper import map_constraints
from src.application.data_sources.data_source_upload_policy import validate_upload
from src.application.data_sources.i_data_source_service import (
    ICsvPreviewReader,
    ICsvUploadValidator,
    IDataSourceFileStore,
    IDataSourceService,
)
from src.application.data_sources.input import (
    DataSourceIdInput,
    ListDataSourcesInput,
    UpdateDataSourceColumnInput,
    UploadDataSourcesInput,
    UploadFileInput,
)
from src.application.data_sources.output import (
    DataSourceListOutput,
    DataSourceOutput,
    PreviewOutput,
    UploadDataSourcesOutput,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import DataSourceType
from src.domain.data_source.i_data_source_repository import IDataSourceRepository
from src.domain.data_source.value_objects import ColumnUpdate
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.shared.types import EntityID
from typing_extensions import override


class DataSourceService(IDataSourceService):
    """Điều phối source storage, authorization và transaction."""

    def __init__(
        self,
        sources: IDataSourceRepository,
        files: IDataSourceFileStore,
        csv_validator: ICsvUploadValidator,
        preview_reader: ICsvPreviewReader,
        unit_of_work: IUnitOfWork,
        access: ProjectAccessPolicy,
        projects: IProjectRepository,
    ) -> None:
        self._sources = sources
        self._files = files
        self._csv_validator = csv_validator
        self._preview_reader = preview_reader
        self._unit_of_work = unit_of_work
        self._access = access
        self._projects = projects

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
        async with self._unit_of_work:
            project = await self._access.require_owner(data.project_id)
            existing = await self._sources.list_by_project(data.project_id)
            by_name = {source.name.casefold(): source for source in existing}
            validate_upload(data, frozenset(by_name))
            for item in data.files:
                self._csv_validator.validate(item.content, item.filename)
            uploaded = await self._process_uploads(data, by_name)
            project.increment_source_revision()
            await self._projects.save(project)
            await self._unit_of_work.commit()
        return UploadDataSourcesOutput(tuple(uploaded), len(data.files))

    async def _process_uploads(
        self,
        data: UploadDataSourcesInput,
        existing: dict[str, DataSource],
    ) -> list[DataSourceOutput]:
        uploaded: list[DataSourceOutput] = []
        for item in data.files:
            key = item.filename.casefold()
            saved = await self._save_csv(data.project_id, item, existing.get(key))
            existing[key] = saved
            uploaded.append(DataSourceOutput.from_domain(saved))
        return uploaded

    async def _save_csv(
        self,
        project_id: EntityID,
        file: UploadFileInput,
        existing: DataSource | None,
    ) -> DataSource:
        location = await self._files.save_file(str(project_id), file.filename, file.content)
        source = existing or DataSource(
            project_id=project_id,
            name=file.filename,
            location=location,
            type=DataSourceType.CSV,
        )
        source.replace_file(location, None)
        return await self._sources.save(source)

    @override
    async def get_preview(self, data: DataSourceIdInput) -> PreviewOutput:
        """Đọc preview CSV nếu actor là thành viên dự án."""
        await self._access.require_member(data.project_id)
        source = await self._get_source(data)
        content = await self._files.read_file(source.location)
        return self._preview_reader.read(content, source.name)

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
        async with self._unit_of_work:
            project = await self._access.require_owner(data.project_id)
            source = await self._get_source(data)
            await self._files.delete_file(source.location)
            await self._sources.delete(source.id)
            await self._files.cleanup_empty_dir(str(data.project_id))
            project.increment_source_revision()
            await self._projects.save(project)
            await self._unit_of_work.commit()

    async def _get_source(self, data: DataSourceIdInput) -> DataSource:
        source = await self._sources.get_by_id(data.data_source_id)
        if source is None or source.project_id != data.project_id:
            raise BusinessException(
                code=ErrorCode.DATA_SOURCE_NOT_FOUND,
                message="Nguồn dữ liệu không tồn tại trong dự án.",
            )
        return source
