"""Module quản lý Nguồn dữ liệu (Data Source Domain)."""

from src.domain.data_source.column_profile import ColumnProfile, LogicalTypeDecision
from src.domain.data_source.column_type_inference import (
    infer_logical_type,
    is_identifier_like,
)
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
    RelationshipType,
)
from src.domain.data_source.i_data_source_repository import IDataSourceRepository
from src.domain.data_source.rules import normalize_data_source_fields
from src.domain.data_source.value_objects import (
    ColumnMetadata,
    ColumnUpdate,
    RelationshipMetadata,
    SchemaMetadata,
    TableMetadata,
)

__all__: list[str] = [
    "DataSource",
    "DataSourceType",
    "RelationshipType",
    "SchemaMetadata",
    "TableMetadata",
    "ColumnMetadata",
    "ColumnDataType",
    "DataSourceAnalysisStatus",
    "ColumnConstraintType",
    "ColumnConstraint",
    "ForeignKeyConstraint",
    "UniqueConstraint",
    "CheckConstraint",
    "DefaultConstraint",
    "RelationshipMetadata",
    "ColumnUpdate",
    "ColumnProfile",
    "LogicalTypeDecision",
    "infer_logical_type",
    "is_identifier_like",
    "IDataSourceRepository",
    "normalize_data_source_fields",
]
