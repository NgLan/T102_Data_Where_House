"""Immutable transformations cho semantic annotations trong SchemaMetadata."""

from dataclasses import dataclass, replace

from src.domain.data_source.schema_components import (
    RelationshipMetadata,
    TableMetadata,
)
from src.domain.data_source.semantic_metadata import (
    SourceSemanticAnnotation,
    merge_semantic_annotation,
    remove_semantic_annotation,
)
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ColumnAnnotationTarget:
    table_name: str
    column_name: str
    annotation: SourceSemanticAnnotation


@dataclass(frozen=True, slots=True)
class RelationshipAnnotationTarget:
    from_column: str
    to_column: str
    annotation: SourceSemanticAnnotation


@dataclass(frozen=True, slots=True)
class AnnotationRemovalTarget:
    requirement_id: EntityID
    concept_key: str


def annotate_schema_column(
    tables: tuple[TableMetadata, ...],
    target: ColumnAnnotationTarget,
) -> tuple[TableMetadata, ...] | None:
    """Ghi annotation lên exact table/column nếu tồn tại."""
    updated: list[TableMetadata] = []
    found = False
    for table in tables:
        columns = []
        for column in table.columns:
            if table.name == target.table_name and column.name == target.column_name:
                values = merge_semantic_annotation(column.semantic_annotations, target.annotation)
                column = replace(column, semantic_annotations=values)
                found = True
            columns.append(column)
        updated.append(replace(table, columns=tuple(columns)))
    return tuple(updated) if found else None


def annotate_schema_relationship(
    relationships: tuple[RelationshipMetadata, ...],
    target: RelationshipAnnotationTarget,
) -> tuple[RelationshipMetadata, ...] | None:
    """Ghi annotation lên exact relationship nếu tồn tại."""
    updated: list[RelationshipMetadata] = []
    found = False
    for relationship in relationships:
        matches = relationship.from_column == target.from_column and relationship.to_column == target.to_column
        if matches:
            values = merge_semantic_annotation(relationship.semantic_annotations, target.annotation)
            relationship = replace(relationship, semantic_annotations=values)
            found = True
        updated.append(relationship)
    return tuple(updated) if found else None


def remove_schema_annotations(
    tables: tuple[TableMetadata, ...],
    relationships: tuple[RelationshipMetadata, ...],
    target: AnnotationRemovalTarget,
) -> tuple[tuple[TableMetadata, ...], tuple[RelationshipMetadata, ...]]:
    """Xóa USER annotation đúng Requirement/concept trên toàn schema."""
    updated_tables = tuple(_remove_table_annotations(item, target) for item in tables)
    updated_relationships = tuple(
        replace(
            item,
            semantic_annotations=remove_semantic_annotation(
                item.semantic_annotations, target.requirement_id, target.concept_key
            ),
        )
        for item in relationships
    )
    return updated_tables, updated_relationships


def _remove_table_annotations(
    table: TableMetadata,
    target: AnnotationRemovalTarget,
) -> TableMetadata:
    columns = tuple(
        replace(
            column,
            semantic_annotations=remove_semantic_annotation(
                column.semantic_annotations, target.requirement_id, target.concept_key
            ),
        )
        for column in table.columns
    )
    return replace(table, columns=columns)
