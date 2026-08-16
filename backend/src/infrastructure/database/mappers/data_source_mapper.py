"""Mapper chuyển đổi dữ liệu giữa DataSource Domain Entity và DataSourceModel Persistence."""

from typing import Any

from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import DataSourceType, RelationshipType
from src.domain.data_source.value_objects import (
    ColumnMetadata,
    RelationshipMetadata,
    SchemaMetadata,
    TableMetadata,
)
from src.infrastructure.database.models.data_source import DataSourceModel


class DataSourceMapper:
    """Mapper thực hiện chuyển đổi giữa DataSource Entity và DataSourceModel."""

    @staticmethod
    def schema_metadata_to_dict(schema: SchemaMetadata | None) -> dict[str, Any] | None:
        """Chuyển đổi SchemaMetadata Value Object sang dict JSONB."""
        if not schema:
            return None

        tables_data = []
        for table in schema.tables:
            cols_data = []
            for col in table.columns:
                cols_data.append(
                    {
                        "name": col.name,
                        "data_type": col.data_type,
                        "primary_key": col.primary_key,
                        "nullable": col.nullable,
                        "unique": col.unique,
                        "foreign_key_reference": col.foreign_key_reference,
                        "default_value": col.default_value,
                        "constraints": list(col.constraints),
                        "description": col.description,
                        "options": list(col.options),
                    }
                )
            tables_data.append({"name": table.name, "columns": cols_data})

        rels_data = []
        for rel in schema.relationships:
            rels_data.append(
                {
                    "from_column": rel.from_column,
                    "to_column": rel.to_column,
                    "type": rel.type.value,
                }
            )

        return {"tables": tables_data, "relationships": rels_data}

    @staticmethod
    def dict_to_schema_metadata(data: dict[str, Any] | None) -> SchemaMetadata | None:
        """Chuyển đổi dict JSONB từ database sang SchemaMetadata Value Object (bảo vệ lỗi KeyError)."""
        if not data or not isinstance(data, dict):
            return None

        tables_list = []
        for tbl in data.get("tables", []):
            if not isinstance(tbl, dict) or "name" not in tbl:
                continue
            cols_list = []
            for col in tbl.get("columns", []):
                if not isinstance(col, dict) or "name" not in col:
                    continue
                cols_list.append(
                    ColumnMetadata(
                        name=col["name"],
                        data_type=col.get("data_type", "TEXT"),
                        primary_key=col.get("primary_key", False),
                        nullable=col.get("nullable", True),
                        unique=col.get("unique", False),
                        foreign_key_reference=col.get("foreign_key_reference"),
                        default_value=col.get("default_value"),
                        constraints=tuple(col.get("constraints", ())),
                        description=col.get("description"),
                        options=tuple(col.get("options", ())),
                    )
                )
            tables_list.append(TableMetadata(name=tbl["name"], columns=tuple(cols_list)))

        rels_list = []
        for rel in data.get("relationships", []):
            if not isinstance(rel, dict):
                continue
            from_col = rel.get("from_column") or rel.get("from_col") or rel.get("source_column") or ""
            to_col = rel.get("to_column") or rel.get("to_col") or rel.get("target_column") or ""
            rel_type_str = rel.get("type", "MANY_TO_ONE")
            try:
                rel_type = RelationshipType(rel_type_str)
            except (ValueError, KeyError):
                rel_type = RelationshipType.MANY_TO_ONE

            if from_col and to_col:
                rels_list.append(
                    RelationshipMetadata(
                        from_column=str(from_col),
                        to_column=str(to_col),
                        type=rel_type,
                    )
                )

        return SchemaMetadata(tables=tuple(tables_list), relationships=tuple(rels_list))

    @classmethod
    def to_domain(cls, model: DataSourceModel) -> DataSource:
        """Chuyển đổi từ DataSourceModel (Persistence) sang DataSource (Domain Entity)."""
        return DataSource(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            location=model.location,
            type=DataSourceType(model.type),
            description=model.description,
            schema_metadata=cls.dict_to_schema_metadata(model.schema_metadata),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @classmethod
    def to_model(cls, entity: DataSource) -> DataSourceModel:
        """Chuyển đổi từ DataSource (Domain Entity) sang DataSourceModel (Persistence)."""
        return DataSourceModel(
            id=entity.id,
            project_id=entity.project_id,
            name=entity.name,
            location=entity.location,
            type=entity.type.value,
            description=entity.description,
            schema_metadata=cls.schema_metadata_to_dict(entity.schema_metadata),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @classmethod
    def update_model(cls, model: DataSourceModel, entity: DataSource) -> DataSourceModel:
        """Cập nhật dữ liệu từ DataSource Entity sang DataSourceModel đã tồn tại."""
        model.name = entity.name
        model.location = entity.location
        model.type = entity.type.value
        model.description = entity.description
        model.schema_metadata = cls.schema_metadata_to_dict(entity.schema_metadata)
        model.updated_at = entity.updated_at
        return model
