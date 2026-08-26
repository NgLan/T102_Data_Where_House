"""Persistence helper cho batch Requirement Documents đã parse."""

from dataclasses import dataclass
from pathlib import Path

from src.application.common.file_mutation_log import FileMutationLog, FileReplacement
from src.application.requirement_files.parsed_requirement_file import ParsedRequirementFile
from src.common.utils.uuid import generate_uuid
from src.domain.requirement_file.entities import RequirementFile
from src.domain.requirement_file.i_requirement_file_repository import (
    IRequirementFileRepository,
)
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class RequirementFileBatchInput:
    """Context cần thiết để persist một upload batch."""

    project_id: EntityID
    parsed: tuple[ParsedRequirementFile, ...]
    existing: tuple[RequirementFile, ...]
    mutations: FileMutationLog


@dataclass(frozen=True, slots=True)
class RequirementFilePersistenceInput:
    """Input persist một file trong batch."""

    project_id: EntityID
    parsed: ParsedRequirementFile
    current: RequirementFile | None
    mutations: FileMutationLog


class RequirementFileBatchPersister:
    """Replace storage objects và upsert metadata theo filename."""

    def __init__(self, files: IRequirementFileRepository) -> None:
        self._files = files

    async def persist(
        self, data: RequirementFileBatchInput
    ) -> tuple[list[RequirementFile], bool]:
        by_name = {item.name.casefold(): item for item in data.existing}
        saved: list[RequirementFile] = []
        changed = False
        for parsed in data.parsed:
            current = by_name.get(parsed.name.casefold())
            item, item_changed = await self._persist_one(
                RequirementFilePersistenceInput(
                    data.project_id, parsed, current, data.mutations
                )
            )
            persisted = await self._files.save(item)
            by_name[parsed.name.casefold()] = persisted
            saved.append(persisted)
            changed = changed or item_changed
        return saved, changed

    async def _persist_one(
        self,
        data: RequirementFilePersistenceInput,
    ) -> tuple[RequirementFile, bool]:
        parsed = data.parsed
        current = data.current
        file_id = current.id if current else generate_uuid()
        location = await data.mutations.replace(
            FileReplacement(
                f"{data.project_id}/requirements",
                _storage_filename(file_id, parsed.name),
                parsed.content,
                current.location if current else None,
            )
        )
        if current is None:
            return RequirementFile(
                id=file_id,
                project_id=data.project_id,
                name=parsed.name,
                file_type=parsed.file_type,
                location=location,
                extracted_text=parsed.extracted_text,
            ), True
        changed = current.name != parsed.name
        current.name = parsed.name
        changed = current.replace(location, parsed.extracted_text) or changed
        current.file_type = parsed.file_type
        return current, changed


def _storage_filename(file_id: EntityID, logical_name: str) -> str:
    """Dùng ID ổn định để tránh collision do filename sanitization."""
    return f"{file_id}{Path(logical_name).suffix.lower()}"
