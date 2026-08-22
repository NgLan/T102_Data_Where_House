"""Mapper chuyển đổi dữ liệu giữa Requirement Domain Entity và RequirementModel Persistence."""

from src.domain.requirement.entities import Requirement
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.infrastructure.database.models.requirement import RequirementModel


class RequirementMapper:
    """Mapper thực hiện chuyển đổi giữa Requirement Entity và RequirementModel."""

    @staticmethod
    def to_domain(model: RequirementModel) -> Requirement:
        """Chuyển đổi từ RequirementModel (Persistence) sang Requirement (Domain Entity)."""
        return Requirement(
            id=model.id,
            project_id=model.project_id,
            type=RequirementType(model.type),
            title=model.title,
            description=model.description,
            priority=RequirementPriority(model.priority),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Requirement) -> RequirementModel:
        """Chuyển đổi từ Requirement (Domain Entity) sang RequirementModel (Persistence)."""
        return RequirementModel(
            id=entity.id,
            project_id=entity.project_id,
            type=entity.type.value,
            title=entity.title,
            description=entity.description,
            priority=entity.priority.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: RequirementModel, entity: Requirement) -> RequirementModel:
        """Cập nhật dữ liệu từ Requirement Entity sang RequirementModel đã tồn tại."""
        model.project_id = entity.project_id
        model.type = entity.type.value
        model.title = entity.title
        model.description = entity.description
        model.priority = entity.priority.value
        model.updated_at = entity.updated_at
        return model
