"""Mapper giữa RequirementFile domain và ORM."""

from src.domain.requirement_file.entities import RequirementFile
from src.domain.requirement_file.enums import RequirementFileType
from src.infrastructure.database.models.requirement_file import RequirementFileModel


class RequirementFileMapper:
    """Mapper persistence của Requirement Document."""

    @staticmethod
    def to_domain(model: RequirementFileModel) -> RequirementFile:
        return RequirementFile(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            file_type=RequirementFileType(model.file_type),
            location=model.location,
            extracted_text=model.extracted_text,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: RequirementFile) -> RequirementFileModel:
        return RequirementFileModel(
            id=entity.id,
            project_id=entity.project_id,
            name=entity.name,
            file_type=entity.file_type.value,
            location=entity.location,
            extracted_text=entity.extracted_text,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def update_model(
        model: RequirementFileModel, entity: RequirementFile
    ) -> RequirementFileModel:
        model.name = entity.name
        model.file_type = entity.file_type.value
        model.location = entity.location
        model.extracted_text = entity.extracted_text
        model.updated_at = entity.updated_at
        return model
