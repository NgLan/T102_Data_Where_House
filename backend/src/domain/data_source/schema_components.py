"""Thành phần vật lý và semantic bên trong SchemaMetadata."""

from dataclasses import dataclass, field

from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_source.constraints import (
    ColumnConstraint,
    normalize_column_constraints,
)
from src.domain.data_source.enums import ColumnDataType, RelationshipType
from src.domain.data_source.semantic_metadata import SourceSemanticAnnotation
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import JsonScalar
from src.domain.shared.value_object import BaseValueObject


@dataclass(frozen=True)
class ColumnMetadata(BaseValueObject):
    """Metadata vật lý, semantic và profile của một cột nguồn dữ liệu."""

    name: str
    data_type: ColumnDataType | str
    primary_key: bool = False
    nullable: bool = True
    constraints: tuple[ColumnConstraint, ...] = field(default_factory=tuple)
    description: str | None = None
    null_count: int = 0
    distinct_count: int = 0
    distinct_values: tuple[JsonScalar, ...] = field(default_factory=tuple)
    is_unique_candidate: bool = False
    is_key_candidate: bool = False
    semantic_annotations: tuple[SourceSemanticAnnotation, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Chuẩn hóa kiểu và đóng băng các collection metadata."""
        value = self.data_type.value if isinstance(self.data_type, ColumnDataType) else self.data_type
        object.__setattr__(self, "data_type", ColumnDataType(value.strip().upper()))
        object.__setattr__(self, "constraints", normalize_column_constraints(self.constraints))
        object.__setattr__(self, "distinct_values", tuple(self.distinct_values))
        object.__setattr__(self, "semantic_annotations", tuple(self.semantic_annotations))


@dataclass(frozen=True)
class TableMetadata(BaseValueObject):
    """Metadata của một bảng trong nguồn dữ liệu."""

    name: str
    columns: tuple[ColumnMetadata, ...] = field(default_factory=tuple)
    row_count: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "columns", tuple(self.columns))


@dataclass(frozen=True)
class RelationshipMetadata(BaseValueObject):
    """Metadata của một mối quan hệ vật lý giữa hai cột."""

    from_column: str
    to_column: str
    type: RelationshipType = RelationshipType.MANY_TO_ONE
    semantic_annotations: tuple[SourceSemanticAnnotation, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        normalized = normalize_str_enum(self.type, RelationshipType, ErrorCode.VALIDATION_ERROR)
        object.__setattr__(self, "type", normalized)
        object.__setattr__(self, "semantic_annotations", tuple(self.semantic_annotations))
