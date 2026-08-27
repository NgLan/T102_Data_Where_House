"""Exact lookup index cho canonical Source Metadata của một LLM invocation."""

from dataclasses import dataclass

from src.domain.data_source.entities import DataSource
from src.domain.data_source.value_objects import SchemaMetadata
from src.domain.shared.types import EntityID
from src.infrastructure.agents.transport_references import TransportReferenceMap


@dataclass(frozen=True, slots=True)
class SchemaMetadataIndex:
    """Ground source/table/column/relationship mà không fuzzy matching."""

    sources: dict[str, DataSource]

    @classmethod
    def create(
        cls,
        data_sources: tuple[DataSource, ...],
        references: TransportReferenceMap,
    ) -> "SchemaMetadataIndex":
        """Index đúng các source thuộc canonical input."""
        sources = {
            reference: source
            for source in data_sources
            if (reference := references.reference_for(source.id)) is not None
        }
        return cls(sources)

    def source_id(self, source_ref: str) -> EntityID | None:
        """Resolve source ref sau khi reference đã được validate."""
        source = self.sources.get(source_ref)
        return source.id if source else None

    def has_table(self, source_ref: str, table_name: str) -> bool:
        """Kiểm tra exact table name trong đúng source."""
        schema = self._schema(source_ref)
        return bool(schema and any(table.name == table_name for table in schema.tables))

    def has_column(self, source_ref: str, table_name: str, column_name: str) -> bool:
        """Kiểm tra exact table/column pair."""
        schema = self._schema(source_ref)
        return bool(
            schema
            and any(
                table.name == table_name and any(column.name == column_name for column in table.columns)
                for table in schema.tables
            )
        )

    def has_relationship(
        self,
        source_ref: str,
        from_column: str,
        to_column: str,
    ) -> bool:
        """Kiểm tra exact relationship endpoints."""
        schema = self._schema(source_ref)
        return bool(
            schema
            and any(item.from_column == from_column and item.to_column == to_column for item in schema.relationships)
        )

    def columns_for(self, source_ref: str, table_name: str) -> tuple[str, ...]:
        """Trả canonical columns để dùng trong retry feedback."""
        schema = self._schema(source_ref)
        if schema is None:
            return ()
        table = next((item for item in schema.tables if item.name == table_name), None)
        return tuple(column.name for column in table.columns) if table else ()

    def _schema(self, source_ref: str) -> SchemaMetadata | None:
        source = self.sources.get(source_ref)
        return source.schema_metadata if source else None
