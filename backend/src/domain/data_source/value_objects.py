"""Value Objects thuộc miền Nguồn dữ liệu (Data Source)."""

from dataclasses import dataclass, field, replace

from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_source.column_update import ColumnUpdate
from src.domain.data_source.constraints import (
    ColumnConstraint,
    normalize_column_constraints,
)
from src.domain.data_source.enums import ColumnDataType, RelationshipType
from src.domain.data_source.semantic_metadata import (
    SourceSemanticAnnotation,
    merge_semantic_annotation,
    remove_semantic_annotation,
)
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID, JsonScalar
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
        data_type = self.data_type.value if isinstance(self.data_type, ColumnDataType) else self.data_type
        object.__setattr__(self, "data_type", ColumnDataType(data_type.strip().upper()))
        object.__setattr__(
            self,
            "constraints",
            normalize_column_constraints(self.constraints),
        )
        object.__setattr__(self, "distinct_values", tuple(self.distinct_values))
        object.__setattr__(self, "semantic_annotations", tuple(self.semantic_annotations))


@dataclass(frozen=True)
class TableMetadata(BaseValueObject):
    """Value Object đại diện cho metadata của một bảng trong nguồn dữ liệu."""

    name: str
    columns: tuple[ColumnMetadata, ...] = field(default_factory=tuple)
    row_count: int = 0

    def __post_init__(self) -> None:
        """Đóng băng danh sách cột được truyền từ parser hoặc mapper."""
        object.__setattr__(self, "columns", tuple(self.columns))


@dataclass(frozen=True)
class RelationshipMetadata(BaseValueObject):
    """Value Object đại diện cho thông tin mối quan hệ giữa các bảng."""

    from_column: str
    to_column: str
    type: RelationshipType = RelationshipType.MANY_TO_ONE
    semantic_annotations: tuple[SourceSemanticAnnotation, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Đảm bảo trường type được parse thành RelationshipType enum nếu khởi tạo từ string."""
        object.__setattr__(
            self,
            "type",
            normalize_str_enum(self.type, RelationshipType, ErrorCode.VALIDATION_ERROR),
        )
        object.__setattr__(self, "semantic_annotations", tuple(self.semantic_annotations))


@dataclass(frozen=True)
class SchemaMetadata(BaseValueObject):
    """Value Object đại diện cho cấu trúc metadata đã bóc tách từ nguồn dữ liệu."""

    tables: tuple[TableMetadata, ...] = field(default_factory=tuple)
    relationships: tuple[RelationshipMetadata, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Đóng băng toàn bộ collection của snapshot schema."""
        object.__setattr__(self, "tables", tuple(self.tables))
        object.__setattr__(self, "relationships", tuple(self.relationships))

    def update_column(self, update: ColumnUpdate) -> "SchemaMetadata | None":
        """Tạo schema mới với một cột đã được cập nhật bất biến.

        Args:
            update: Thay đổi cột đã được chuẩn hóa.

        Returns:
            Snapshot schema mới hoặc ``None`` nếu không tìm thấy cột.
        """
        tables: list[TableMetadata] = []
        found = False
        for table in self.tables:
            columns = []
            for column in table.columns:
                if table.name == update.table_name and column.name == update.column_name:
                    column = _replace_column(column, update)
                    found = True
                columns.append(column)
            tables.append(
                TableMetadata(
                    name=table.name,
                    columns=tuple(columns),
                    row_count=table.row_count,
                )
            )
        if not found:
            return None
        return SchemaMetadata(tables=tuple(tables), relationships=self.relationships)

    def annotate_column(
        self,
        table_name: str,
        column_name: str,
        annotation: SourceSemanticAnnotation,
    ) -> "SchemaMetadata | None":
        """Ghi semantic decision lên đúng column và giữ nguyên profile metadata."""
        update = _annotate_column(self.tables, table_name, column_name, annotation)
        if update is None:
            return None
        return SchemaMetadata(update, self.relationships)

    def annotate_relationship(
        self,
        from_column: str,
        to_column: str,
        annotation: SourceSemanticAnnotation,
    ) -> "SchemaMetadata | None":
        """Ghi semantic decision lên đúng relationship hiện hữu."""
        relationships = _annotate_relationship(
            self.relationships, from_column, to_column, annotation
        )
        if relationships is None:
            return None
        return SchemaMetadata(self.tables, relationships)

    def remove_user_annotation(
        self, requirement_id: EntityID, concept_key: str
    ) -> "SchemaMetadata":
        """Xóa scoped USER annotation nhưng giữ nguyên profile metadata."""
        tables = tuple(
            replace(
                table,
                columns=tuple(
                    replace(
                        column,
                        semantic_annotations=remove_semantic_annotation(
                            column.semantic_annotations, requirement_id, concept_key
                        ),
                    )
                    for column in table.columns
                ),
            )
            for table in self.tables
        )
        relationships = tuple(
            replace(
                item,
                semantic_annotations=remove_semantic_annotation(
                    item.semantic_annotations, requirement_id, concept_key
                ),
            )
            for item in self.relationships
        )
        return SchemaMetadata(tables, relationships)


def _replace_column(
    column: ColumnMetadata,
    update: ColumnUpdate,
) -> ColumnMetadata:
    """Giữ nguyên metadata không được phép chỉnh từ màn hình khởi tạo."""
    return replace(
        column,
        data_type=update.data_type or column.data_type,
        distinct_values=(update.distinct_values if update.distinct_values is not None else column.distinct_values),
        constraints=(update.constraints if update.constraints is not None else column.constraints),
    )


def _annotate_column(
    tables: tuple[TableMetadata, ...],
    table_name: str,
    column_name: str,
    annotation: SourceSemanticAnnotation,
) -> tuple[TableMetadata, ...] | None:
    updated: list[TableMetadata] = []
    found = False
    for table in tables:
        columns = []
        for column in table.columns:
            if table.name == table_name and column.name == column_name:
                values = merge_semantic_annotation(column.semantic_annotations, annotation)
                column = replace(column, semantic_annotations=values)
                found = True
            columns.append(column)
        updated.append(replace(table, columns=tuple(columns)))
    return tuple(updated) if found else None


def _annotate_relationship(
    relationships: tuple[RelationshipMetadata, ...],
    from_column: str,
    to_column: str,
    annotation: SourceSemanticAnnotation,
) -> tuple[RelationshipMetadata, ...] | None:
    updated = []
    found = False
    for relationship in relationships:
        if relationship.from_column == from_column and relationship.to_column == to_column:
            values = merge_semantic_annotation(relationship.semantic_annotations, annotation)
            relationship = replace(relationship, semantic_annotations=values)
            found = True
        updated.append(relationship)
    return tuple(updated) if found else None
