"""Output models độc lập HTTP cho Data Source application service."""

from dataclasses import dataclass

from src.domain.data_source.entities import DataSource
from src.domain.data_source.value_objects import SchemaMetadata, TableMetadata
from src.domain.shared.types import EntityID


@dataclass(frozen=True)
class DataSourceOutput:
    """Nguồn dữ liệu không làm lộ storage location."""

    id: EntityID
    project_id: EntityID
    name: str
    type: str
    description: str | None
    schema_metadata: SchemaMetadata | None

    @property
    def tables(self) -> tuple[TableMetadata, ...]:
        """Cung cấp Domain table value objects cho response mapper."""
        return self.schema_metadata.tables if self.schema_metadata else ()

    @classmethod
    def from_domain(cls, source: DataSource) -> "DataSourceOutput":
        """Ánh xạ entity sang output ổn định."""
        return cls(
            id=source.id,
            project_id=source.project_id,
            name=source.name,
            type=source.type.value,
            description=source.description,
            schema_metadata=source.schema_metadata,
        )


@dataclass(frozen=True)
class PreviewOutput:
    """Dữ liệu xem trước được đọc từ file gốc."""

    rows: tuple[dict[str, str | None], ...]
    total_rows: int


@dataclass(frozen=True)
class DataSourceListOutput:
    """Danh sách nguồn dữ liệu kèm quyền chỉnh sửa của actor hiện tại."""

    items: tuple[DataSourceOutput, ...]
    can_edit: bool


@dataclass(frozen=True)
class UploadDataSourcesOutput:
    """Kết quả upload batch."""

    data_sources: tuple[DataSourceOutput, ...]
    extracted_requirement_text: str | None
    total_files_processed: int
