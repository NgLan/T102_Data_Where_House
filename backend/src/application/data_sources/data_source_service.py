"""Application service duy nhất cho module Data Source."""

from dataclasses import dataclass

from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_sources.data_source_access import DataSourceAccess
from src.application.data_sources.data_source_rules import (
    extension_of,
    validate_column,
    validate_upload,
)
from src.application.data_sources.i_data_source_file_store import IDataSourceFileStore
from src.application.data_sources.i_data_source_service import IDataSourceService
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
from src.common.exceptions.base import AppException
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import DataSourceType
from src.domain.data_source.file_parser import IFileParserService
from src.domain.data_source.repository import IDataSourceRepository
from src.domain.project.repository import IProjectMemberRepository, IProjectRepository
from src.domain.shared.types import EntityID
from typing_extensions import override


@dataclass(frozen=True)
class DataSourceServiceDependencies:
    """Outbound dependencies của Data Source service."""

    projects: IProjectRepository
    members: IProjectMemberRepository
    sources: IDataSourceRepository
    files: IDataSourceFileStore
    parser: IFileParserService
    unit_of_work: IUnitOfWork


class DataSourceService(IDataSourceService):
    """Điều phối upload, preview, schema, authorization và transaction."""

    def __init__(self, dependencies: DataSourceServiceDependencies, actor_id: EntityID) -> None:
        self._deps = dependencies
        self._access = DataSourceAccess(dependencies.projects, dependencies.members, actor_id)

    @override
    async def list_data_sources(self, data: ListDataSourcesInput) -> DataSourceListOutput:
        can_edit = await self._access.require_member(data.project_id)
        sources = await self._deps.sources.list_by_project(data.project_id)
        return DataSourceListOutput(
            items=tuple(DataSourceOutput.from_domain(source) for source in sources),
            can_edit=can_edit,
        )

    @override
    async def upload_data_sources(self, data: UploadDataSourcesInput) -> UploadDataSourcesOutput:
        await self._access.require_owner(data.project_id)
        validate_upload(data)
        existing = await self._deps.sources.list_by_project(data.project_id)
        by_name = {source.name.casefold(): source for source in existing}
        uploaded: list[DataSourceOutput] = []
        requirements: list[str] = []
        try:
            for item in data.files:
                if extension_of(item.filename) == ".docx":
                    requirements.append(self._deps.parser.parse_docx(item.content, item.filename).content)
                    continue
                source = await self._save_csv(data.project_id, item, by_name.get(item.filename.casefold()))
                uploaded.append(DataSourceOutput.from_domain(source))
            await self._deps.unit_of_work.commit()
        except AppException:
            await self._deps.unit_of_work.rollback()
            raise
        text = "\n\n---\n\n".join(part for part in requirements if part) or None
        return UploadDataSourcesOutput(tuple(uploaded), text, len(data.files))

    @override
    async def get_preview(self, data: DataSourceIdInput) -> PreviewOutput:
        await self._access.require_member(data.project_id)
        source = await self._get_source(data)
        content = await self._deps.files.read_file(source.location)
        parsed = self._deps.parser.parse_csv(content, source.name, source.location)
        rows = tuple({key: _preview_value(value) for key, value in row.items()} for row in parsed.preview_rows)
        return PreviewOutput(rows=rows, total_rows=parsed.total_rows)

    @override
    async def update_column(self, data: UpdateDataSourceColumnInput) -> DataSourceOutput:
        await self._access.require_owner(data.project_id)
        try:
            source = await self._get_source(DataSourceIdInput(data.project_id, data.data_source_id))
            options = validate_column(data.data_type, data.options)
            if not source.update_column(data.table_name, data.column_name, data.data_type, options):
                raise BusinessException(
                    code=ErrorCode.DATA_SOURCE_COLUMN_NOT_FOUND,
                    message="Không tìm thấy cột trong nguồn dữ liệu.",
                )
            saved = await self._deps.sources.save(source)
            await self._deps.unit_of_work.commit()
            return DataSourceOutput.from_domain(saved)
        except AppException:
            await self._deps.unit_of_work.rollback()
            raise

    @override
    async def delete_data_source(self, data: DataSourceIdInput) -> None:
        await self._access.require_owner(data.project_id)
        try:
            source = await self._get_source(data)
            await self._deps.files.delete_file(source.location)
            await self._deps.sources.delete(source.id)
            await self._deps.unit_of_work.commit()
        except AppException:
            await self._deps.unit_of_work.rollback()
            raise
        await self._deps.files.cleanup_empty_dir(str(data.project_id))

    async def _save_csv(
        self,
        project_id: EntityID,
        item: UploadFileInput,
        existing: DataSource | None,
    ) -> DataSource:
        parsed = self._deps.parser.parse_csv(item.content, item.filename, "")
        location = await self._deps.files.save_file(str(project_id), item.filename, item.content)
        source = existing or DataSource(
            project_id=project_id,
            name=item.filename,
            location=location,
            type=DataSourceType.CSV,
        )
        source.replace_file(location, parsed.schema_metadata)
        return await self._deps.sources.save(source)

    async def _get_source(self, data: DataSourceIdInput) -> DataSource:
        source = await self._deps.sources.get_by_id(data.data_source_id)
        if source is None or source.project_id != data.project_id:
            raise BusinessException(
                code=ErrorCode.DATA_SOURCE_NOT_FOUND,
                message="Nguồn dữ liệu không tồn tại trong dự án.",
            )
        return source


def _preview_value(value: object) -> str | None:
    return None if value is None else str(value)
