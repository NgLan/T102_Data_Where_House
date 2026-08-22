"""Mapper giữa DataSource Domain entity và ORM model."""

from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import DataSourceType
from src.infrastructure.database.mappers.data_source.schema_metadata_codec import (
    decode_schema_metadata,
    encode_schema_metadata,
)
from src.infrastructure.database.models.data_source import DataSourceModel


class DataSourceMapper:
    """Ánh xạ DataSource mà không chứa quy tắc nghiệp vụ."""

    @staticmethod
    def to_domain(model: DataSourceModel) -> DataSource:
        """Khôi phục DataSource từ ORM model."""
        return DataSource(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            location=model.location,
            type=DataSourceType(model.type),
            description=model.description,
            schema_metadata=decode_schema_metadata(model.schema_metadata),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: DataSource) -> DataSourceModel:
        """Tạo ORM model từ DataSource."""
        return DataSourceModel(
            id=entity.id,
            project_id=entity.project_id,
            name=entity.name,
            location=entity.location,
            type=entity.type.value,
            description=entity.description,
            schema_metadata=encode_schema_metadata(entity.schema_metadata),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: DataSourceModel, entity: DataSource) -> DataSourceModel:
        """Cập nhật các trường có thể thay đổi của ORM model."""
        model.name = entity.name
        model.location = entity.location
        model.type = entity.type.value
        model.description = entity.description
        model.schema_metadata = encode_schema_metadata(entity.schema_metadata)
        model.updated_at = entity.updated_at
        return model
