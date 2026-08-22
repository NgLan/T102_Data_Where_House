"""Mapper chuyển đổi dữ liệu giữa DataModelChange Domain Entity và DataModelChangeModel Persistence."""

from src.domain.data_model.entities import DataModelChange
from src.domain.data_model.enums import DataModelChangeStatus
from src.infrastructure.database.models.data_model_change import DataModelChangeModel


class DataModelChangeMapper:
    """Mapper thực hiện chuyển đổi giữa DataModelChange Entity và DataModelChangeModel."""

    @staticmethod
    def to_domain(model: DataModelChangeModel) -> DataModelChange:
        """Chuyển đổi từ DataModelChangeModel (Persistence) sang DataModelChange (Domain Entity)."""
        return DataModelChange(
            id=model.id,
            data_model_id=model.data_model_id,
            user_id=model.user_id,
            base_revision=model.base_revision,
            base_dbml=model.base_dbml,
            proposed_dbml=model.proposed_dbml,
            status=DataModelChangeStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: DataModelChange) -> DataModelChangeModel:
        """Chuyển đổi từ DataModelChange (Domain Entity) sang DataModelChangeModel (Persistence)."""
        return DataModelChangeModel(
            id=entity.id,
            data_model_id=entity.data_model_id,
            user_id=entity.user_id,
            base_revision=entity.base_revision,
            base_dbml=entity.base_dbml,
            proposed_dbml=entity.proposed_dbml,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: DataModelChangeModel, entity: DataModelChange) -> DataModelChangeModel:
        """Cập nhật dữ liệu từ DataModelChange Entity sang DataModelChangeModel đã tồn tại."""
        model.data_model_id = entity.data_model_id
        model.user_id = entity.user_id
        model.base_revision = entity.base_revision
        model.base_dbml = entity.base_dbml
        model.proposed_dbml = entity.proposed_dbml
        model.status = entity.status.value
        model.updated_at = entity.updated_at
        return model
