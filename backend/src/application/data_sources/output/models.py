"""Output models độc lập HTTP cho Data Source application service."""

from dataclasses import dataclass
from typing import TypeAlias

from src.domain.data_source.constraints import (
    CheckConstraint,
    ColumnConstraint,
    DefaultConstraint,
    ForeignKeyConstraint,
    UniqueConstraint,
)
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import (
    ColumnConstraintType,
    ColumnDataType,
    DataSourceAnalysisStatus,
    DataSourceType,
)
from src.domain.data_source.value_objects import ColumnMetadata, TableMetadata
from src.domain.shared.types import EntityID, JsonScalar


@dataclass(frozen=True, slots=True)
class ForeignKeyConstraintOutput:
    """Output constraint khóa ngoại."""

    type: ColumnConstraintType
    reference_table: str
    reference_column: str


@dataclass(frozen=True, slots=True)
class UniqueConstraintOutput:
    """Output constraint duy nhất."""

    type: ColumnConstraintType


@dataclass(frozen=True, slots=True)
class CheckConstraintOutput:
    """Output constraint kiểm tra."""

    type: ColumnConstraintType
    expression: str


@dataclass(frozen=True, slots=True)
class DefaultConstraintOutput:
    """Output constraint giá trị mặc định."""

    type: ColumnConstraintType
    value: JsonScalar


ColumnConstraintOutput: TypeAlias = (
    ForeignKeyConstraintOutput | UniqueConstraintOutput | CheckConstraintOutput | DefaultConstraintOutput
)


@dataclass(frozen=True, slots=True)
class DataSourceColumnOutput:
    """Metadata cột độc lập Domain entity."""

    name: str
    data_type: ColumnDataType
    nullable: bool
    primary_key: bool
    null_count: int
    distinct_count: int
    distinct_values: tuple[JsonScalar, ...]
    constraints: tuple[ColumnConstraintOutput, ...]
    is_unique_candidate: bool
    is_key_candidate: bool

    @classmethod
    def from_domain(cls, column: ColumnMetadata) -> "DataSourceColumnOutput":
        """Ánh xạ cột Domain sang application output."""
        return cls(
            name=column.name,
            data_type=column.data_type,
            nullable=column.nullable,
            primary_key=column.primary_key,
            null_count=column.null_count,
            distinct_count=column.distinct_count,
            distinct_values=column.distinct_values,
            constraints=tuple(_constraint_output(item) for item in column.constraints),
            is_unique_candidate=column.is_unique_candidate,
            is_key_candidate=column.is_key_candidate,
        )


@dataclass(frozen=True, slots=True)
class DataSourceTableOutput:
    """Metadata bảng độc lập Domain value object."""

    name: str
    columns: tuple[DataSourceColumnOutput, ...]

    @classmethod
    def from_domain(cls, table: TableMetadata) -> "DataSourceTableOutput":
        """Ánh xạ bảng Domain sang application output."""
        return cls(
            name=table.name,
            columns=tuple(DataSourceColumnOutput.from_domain(item) for item in table.columns),
        )


@dataclass(frozen=True, slots=True)
class DataSourceOutput:
    """Nguồn dữ liệu không làm lộ storage location."""

    id: EntityID
    project_id: EntityID
    name: str
    type: DataSourceType
    description: str | None
    tables: tuple[DataSourceTableOutput, ...]
    analysis_status: DataSourceAnalysisStatus

    @classmethod
    def from_domain(cls, source: DataSource) -> "DataSourceOutput":
        """Ánh xạ entity sang output ổn định."""
        return cls(
            id=source.id,
            project_id=source.project_id,
            name=source.name,
            type=source.type,
            description=source.description,
            tables=tuple(
                DataSourceTableOutput.from_domain(table)
                for table in (source.schema_metadata.tables if source.schema_metadata else ())
            ),
            analysis_status=(
                DataSourceAnalysisStatus.READY
                if source.schema_metadata is not None
                else DataSourceAnalysisStatus.PENDING
            ),
        )


@dataclass(frozen=True, slots=True)
class PreviewOutput:
    """Dữ liệu xem trước được đọc từ file gốc."""

    rows: tuple[dict[str, str | None], ...]
    total_rows: int


@dataclass(frozen=True, slots=True)
class DataSourceListOutput:
    """Danh sách nguồn dữ liệu kèm quyền chỉnh sửa của actor hiện tại."""

    items: tuple[DataSourceOutput, ...]
    can_edit: bool


@dataclass(frozen=True, slots=True)
class UploadDataSourcesOutput:
    """Kết quả upload batch file nguồn dữ liệu."""

    data_sources: tuple[DataSourceOutput, ...]
    total_files_uploaded: int


def _constraint_output(constraint: ColumnConstraint) -> ColumnConstraintOutput:
    """Ánh xạ từng biến thể constraint sang output tương ứng."""
    if isinstance(constraint, ForeignKeyConstraint):
        return ForeignKeyConstraintOutput(
            constraint.type,
            constraint.reference_table,
            constraint.reference_column,
        )
    if isinstance(constraint, UniqueConstraint):
        return UniqueConstraintOutput(constraint.type)
    if isinstance(constraint, CheckConstraint):
        return CheckConstraintOutput(constraint.type, constraint.expression)
    if isinstance(constraint, DefaultConstraint):
        return DefaultConstraintOutput(constraint.type, constraint.value)
    raise TypeError(f"Constraint không được hỗ trợ: {type(constraint).__name__}")
