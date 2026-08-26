"""HTTP-independent inputs cho Requirement Documents."""

from dataclasses import dataclass

from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ListRequirementFilesInput:
    project_id: EntityID


@dataclass(frozen=True, slots=True)
class RequirementUploadInput:
    filename: str
    content: bytes


@dataclass(frozen=True, slots=True)
class UploadRequirementFilesInput:
    project_id: EntityID
    files: tuple[RequirementUploadInput, ...]
    expected_revision: int


@dataclass(frozen=True, slots=True)
class DeleteRequirementFileInput:
    project_id: EntityID
    file_id: EntityID
    expected_revision: int
