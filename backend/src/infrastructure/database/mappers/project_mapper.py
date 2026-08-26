"""Mapper chuyển đổi dữ liệu giữa Project Domain Entity và ProjectModel Persistence."""

from src.domain.project.entities import Project
from src.domain.project.enums import ProjectStatus
from src.infrastructure.database.models.project import ProjectModel


class ProjectMapper:
    """Mapper thực hiện chuyển đổi giữa Project Entity và ProjectModel."""

    @staticmethod
    def to_domain(model: ProjectModel) -> Project:
        """Chuyển đổi từ ProjectModel (Persistence) sang Project (Domain Entity)."""
        return Project(
            id=model.id,
            name=model.name,
            requirement=model.requirement,
            requirement_revision=model.requirement_revision,
            source_revision=model.source_revision,
            analyzed_requirement_revision=model.analyzed_requirement_revision,
            confirmed_requirement_revision=model.confirmed_requirement_revision,
            derived_analytical_requirement_revision=model.derived_analytical_requirement_revision,
            analyzed_source_revision=model.analyzed_source_revision,
            covered_analytical_requirement_revision=model.covered_analytical_requirement_revision,
            user_id=model.user_id,
            description=model.description,
            domain=model.domain,
            status=ProjectStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Project) -> ProjectModel:
        """Chuyển đổi từ Project (Domain Entity) sang ProjectModel (Persistence)."""
        return ProjectModel(
            id=entity.id,
            name=entity.name,
            requirement=entity.requirement,
            requirement_revision=entity.requirement_revision,
            source_revision=entity.source_revision,
            analyzed_requirement_revision=entity.analyzed_requirement_revision,
            confirmed_requirement_revision=entity.confirmed_requirement_revision,
            derived_analytical_requirement_revision=entity.derived_analytical_requirement_revision,
            analyzed_source_revision=entity.analyzed_source_revision,
            covered_analytical_requirement_revision=entity.covered_analytical_requirement_revision,
            user_id=entity.user_id,
            description=entity.description,
            domain=entity.domain,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(model: ProjectModel, entity: Project) -> ProjectModel:
        """Cập nhật dữ liệu từ Project Entity sang ProjectModel đã tồn tại."""
        model.name = entity.name
        model.requirement = entity.requirement
        model.requirement_revision = entity.requirement_revision
        model.source_revision = entity.source_revision
        model.analyzed_requirement_revision = entity.analyzed_requirement_revision
        model.confirmed_requirement_revision = entity.confirmed_requirement_revision
        model.derived_analytical_requirement_revision = entity.derived_analytical_requirement_revision
        model.analyzed_source_revision = entity.analyzed_source_revision
        model.covered_analytical_requirement_revision = (
            entity.covered_analytical_requirement_revision
        )
        model.description = entity.description
        model.domain = entity.domain
        model.status = entity.status.value
        model.updated_at = entity.updated_at
        return model
