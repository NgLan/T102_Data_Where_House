"""Safe outputs cho Requirement Documents."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.requirement_file.entities import RequirementFile
from src.domain.requirement_file.enums import RequirementFileType
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class RequirementFileOutput:
    id: EntityID
    project_id: EntityID
    name: str
    file_type: RequirementFileType
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, item: RequirementFile) -> "RequirementFileOutput":
        return cls(
            item.id,
            item.project_id,
            item.name,
            item.file_type,
            item.created_at,
            item.updated_at,
        )


@dataclass(frozen=True, slots=True)
class RequirementFileListOutput:
    items: tuple[RequirementFileOutput, ...]
    can_edit: bool


@dataclass(frozen=True, slots=True)
class UploadRequirementFilesOutput:
    items: tuple[RequirementFileOutput, ...]
    requirement_revision: int
