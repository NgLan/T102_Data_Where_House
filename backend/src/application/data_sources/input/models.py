"""Input models độc lập HTTP cho Data Source application service."""

from dataclasses import dataclass, field

from src.domain.shared.types import EntityID


@dataclass(frozen=True)
class ListDataSourcesInput:
    """Input liệt kê nguồn dữ liệu của dự án."""

    project_id: EntityID


@dataclass(frozen=True)
class DataSourceIdInput:
    """Input định danh một nguồn trong dự án."""

    project_id: EntityID
    data_source_id: EntityID


@dataclass(frozen=True)
class UploadFileInput:
    """Nội dung file đã được đọc tại HTTP boundary."""

    filename: str
    content: bytes


@dataclass(frozen=True)
class UploadDataSourcesInput:
    """Input upload một batch CSV hoặc DOCX."""

    project_id: EntityID
    files: tuple[UploadFileInput, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class UpdateDataSourceColumnInput:
    """Input chỉnh metadata một cột nguồn."""

    project_id: EntityID
    data_source_id: EntityID
    table_name: str
    column_name: str
    data_type: str
    options: tuple[str, ...] = field(default_factory=tuple)
