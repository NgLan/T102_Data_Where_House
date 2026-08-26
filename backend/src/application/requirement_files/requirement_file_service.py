"""Application service cho Requirement Documents."""

from pathlib import Path

from src.application.common.file_mutation_log import FileMutationLog
from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.requirement_files.i_requirement_file_service import (
    IRequirementDocumentParser,
    IRequirementFileService,
    IRequirementFileStore,
)
from src.application.requirement_files.input import (
    DeleteRequirementFileInput,
    ListRequirementFilesInput,
    UploadRequirementFilesInput,
)
from src.application.requirement_files.output import (
    RequirementFileListOutput,
    RequirementFileOutput,
    UploadRequirementFilesOutput,
)
from src.application.requirement_files.parsed_requirement_file import ParsedRequirementFile
from src.application.requirement_files.requirement_file_batch_persister import (
    RequirementFileBatchInput,
    RequirementFileBatchPersister,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.requirement_file.entities import RequirementFile
from src.domain.requirement_file.i_requirement_file_repository import (
    IRequirementFileRepository,
)
from src.domain.shared.types import EntityID
from typing_extensions import override

MAX_REQUIREMENT_FILES = 20
MAX_REQUIREMENT_FILE_SIZE = 20 * 1024 * 1024
REQUIREMENT_FILE_DIRECTORY = "requirements"


class RequirementFileService(IRequirementFileService):
    """Điều phối parse, storage, persistence và Requirement revision."""

    def __init__(
        self,
        files: IRequirementFileRepository,
        storage: IRequirementFileStore,
        parser: IRequirementDocumentParser,
        projects: IProjectRepository,
        unit_of_work: IUnitOfWork,
        access: ProjectAccessPolicy,
    ) -> None:
        self._files = files
        self._storage = storage
        self._parser = parser
        self._projects = projects
        self._unit_of_work = unit_of_work
        self._access = access
        self._batch_persister = RequirementFileBatchPersister(files)

    @override
    async def list_files(
        self, data: ListRequirementFilesInput
    ) -> RequirementFileListOutput:
        access = await self._access.require_member(data.project_id)
        files = await self._files.list_by_project(data.project_id)
        return RequirementFileListOutput(
            tuple(RequirementFileOutput.from_domain(item) for item in files),
            access.can_edit,
        )

    @override
    async def upload_files(
        self, data: UploadRequirementFilesInput
    ) -> UploadRequirementFilesOutput:
        parsed = self._parse_batch(data)
        mutations = FileMutationLog(self._storage)
        try:
            saved, revision = await self._upload_transaction(data, parsed, mutations)
        except Exception:
            await mutations.rollback()
            raise
        return UploadRequirementFilesOutput(
            tuple(RequirementFileOutput.from_domain(item) for item in saved),
            revision,
        )

    async def _upload_transaction(
        self,
        data: UploadRequirementFilesInput,
        parsed: tuple[ParsedRequirementFile, ...],
        mutations: FileMutationLog,
    ) -> tuple[list[RequirementFile], int]:
        async with self._unit_of_work:
            project = await self._access.require_owner_for_update(data.project_id)
            _ensure_revision(project.requirement_revision, data.expected_revision)
            existing = await self._files.list_by_project(data.project_id)
            self._validate_capacity(existing, parsed)
            saved, changed = await self._batch_persister.persist(
                RequirementFileBatchInput(
                    data.project_id, parsed, tuple(existing), mutations
                )
            )
            if changed:
                project.increment_requirement_revision()
                await self._projects.save(project)
            await self._unit_of_work.commit()
        return saved, project.requirement_revision

    @override
    async def delete_file(self, data: DeleteRequirementFileInput) -> None:
        mutations = FileMutationLog(self._storage)
        directory = _storage_directory(data.project_id)
        try:
            async with self._unit_of_work:
                project = await self._access.require_owner_for_update(data.project_id)
                _ensure_revision(project.requirement_revision, data.expected_revision)
                item = await self._files.get_by_id(data.file_id)
                if item is None or item.project_id != data.project_id:
                    _raise_file_not_found()
                await mutations.remove(
                    directory, Path(item.location).name, item.location
                )
                await self._files.delete(item.id)
                project.increment_requirement_revision()
                await self._projects.save(project)
                await self._unit_of_work.commit()
        except Exception:
            await mutations.rollback()
            raise
        await self._storage.cleanup_empty_dir(directory)

    def _parse_batch(
        self, data: UploadRequirementFilesInput
    ) -> tuple[ParsedRequirementFile, ...]:
        if not data.files or len(data.files) > MAX_REQUIREMENT_FILES:
            raise BusinessException(
                ErrorCode.MAX_FILES_EXCEEDED,
                "Chỉ được upload tối đa 20 Requirement Documents.",
            )
        names = [item.filename.strip().casefold() for item in data.files]
        if len(names) != len(set(names)):
            raise BusinessException(
                ErrorCode.VALIDATION_ERROR,
                "Batch upload có filename bị trùng.",
            )
        parsed: list[ParsedRequirementFile] = []
        for item in data.files:
            if len(item.content) > MAX_REQUIREMENT_FILE_SIZE:
                raise BusinessException(
                    ErrorCode.FILE_TOO_LARGE,
                    "Requirement Document vượt quá 20 MB.",
                )
            file_type, text = self._parser.parse(item.filename, item.content)
            parsed.append(
                ParsedRequirementFile(
                    item.filename.strip(), item.content, file_type, text
                )
            )
        return tuple(parsed)

    @staticmethod
    def _validate_capacity(
        existing: list[RequirementFile],
        parsed: tuple[ParsedRequirementFile, ...],
    ) -> None:
        existing_names = {item.name.casefold() for item in existing}
        new_count = sum(
            1 for item in parsed if item.name.casefold() not in existing_names
        )
        if len(existing) + new_count > MAX_REQUIREMENT_FILES:
            raise BusinessException(
                ErrorCode.MAX_FILES_EXCEEDED,
                "Project chỉ được có tối đa 20 Requirement Documents.",
            )

def _storage_directory(project_id: EntityID) -> str:
    return f"{project_id}/{REQUIREMENT_FILE_DIRECTORY}"


def _raise_file_not_found() -> None:
    raise BusinessException(
        ErrorCode.REQUIREMENT_FILE_NOT_FOUND,
        "Requirement Document không tồn tại trong Project.",
    )


def _ensure_revision(current: int, expected: int) -> None:
    if current != expected:
        raise BusinessException(
            ErrorCode.REQUIREMENT_REVISION_CONFLICT,
            "Requirement revision không còn hiện hành.",
        )
