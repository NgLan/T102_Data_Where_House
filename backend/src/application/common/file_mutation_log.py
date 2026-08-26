"""Compensation log cho filesystem mutation cạnh database UoW."""

from dataclasses import dataclass

from src.application.common.i_file_store import IFileStore


@dataclass(frozen=True, slots=True)
class _FileMutation:
    project_id: str
    filename: str
    previous_location: str | None
    previous_content: bytes | None
    written_location: str | None


@dataclass(frozen=True, slots=True)
class FileReplacement:
    project_id: str
    filename: str
    content: bytes
    previous_location: str | None


class FileMutationLog:
    """Ghi các file write/delete có thể rollback."""

    def __init__(self, files: IFileStore) -> None:
        self._files = files
        self._mutations: list[_FileMutation] = []

    async def replace(self, replacement: FileReplacement) -> str:
        previous = await self._read_optional(replacement.previous_location)
        location = await self._files.save_file(
            replacement.project_id, replacement.filename, replacement.content
        )
        if replacement.previous_location and replacement.previous_location != location:
            await self._files.delete_file(replacement.previous_location)
        self._mutations.append(
            _FileMutation(
                replacement.project_id,
                replacement.filename,
                replacement.previous_location,
                previous,
                location,
            )
        )
        return location

    async def remove(self, project_id: str, filename: str, location: str) -> None:
        previous = await self._files.read_file(location)
        await self._files.delete_file(location)
        self._mutations.append(
            _FileMutation(project_id, filename, location, previous, None)
        )

    async def rollback(self) -> None:
        for mutation in reversed(self._mutations):
            await self._rollback_one(mutation)
        self._mutations.clear()

    async def _rollback_one(self, mutation: _FileMutation) -> None:
        if mutation.previous_content is None:
            if mutation.written_location:
                await self._files.delete_file(mutation.written_location)
            return
        if mutation.written_location != mutation.previous_location:
            if mutation.written_location:
                await self._files.delete_file(mutation.written_location)
        await self._files.save_file(
            mutation.project_id, mutation.filename, mutation.previous_content
        )

    async def _read_optional(self, location: str | None) -> bytes | None:
        return await self._files.read_file(location) if location else None
