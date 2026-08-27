"""Value Objects thuộc miền Nguồn dữ liệu (Data Source)."""

from dataclasses import dataclass, field, replace

from src.domain.data_source.column_update import ColumnUpdate
from src.domain.data_source.schema_annotation_rules import (
    AnnotationRemovalTarget,
    ColumnAnnotationTarget,
    RelationshipAnnotationTarget,
    annotate_schema_column,
    annotate_schema_relationship,
    remove_schema_annotations,
)
from src.domain.data_source.schema_components import (
    ColumnMetadata,
    RelationshipMetadata,
    TableMetadata,
)
from src.domain.data_source.semantic_metadata import SourceSemanticAnnotation
from src.domain.shared.types import EntityID
from src.domain.shared.value_object import BaseValueObject


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
        target = ColumnAnnotationTarget(table_name, column_name, annotation)
        update = annotate_schema_column(self.tables, target)
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
        target = RelationshipAnnotationTarget(from_column, to_column, annotation)
        relationships = annotate_schema_relationship(
            self.relationships,
            target,
        )
        if relationships is None:
            return None
        return SchemaMetadata(self.tables, relationships)

    def remove_user_annotation(self, requirement_id: EntityID, concept_key: str) -> "SchemaMetadata":
        """Xóa scoped USER annotation nhưng giữ nguyên profile metadata."""
        target = AnnotationRemovalTarget(requirement_id, concept_key)
        tables, relationships = remove_schema_annotations(
            self.tables,
            self.relationships,
            target,
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
