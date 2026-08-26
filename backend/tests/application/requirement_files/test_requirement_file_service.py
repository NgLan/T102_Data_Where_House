"""Requirement file upload, replacement, revision and compensation contracts."""

from uuid import UUID, uuid4

import pytest
from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.requirement_files.input import (
    DeleteRequirementFileInput,
    RequirementUploadInput,
    UploadRequirementFilesInput,
)
from src.application.requirement_files.requirement_file_service import (
    RequirementFileService,
)
from src.domain.project.entities import Project
from src.domain.requirement_file.entities import RequirementFile
from src.infrastructure.parsers.requirement_document_parser import (
    RequirementDocumentParser,
)

from tests.fakes import (
    FakeProjectMemberRepository,
    FakeProjectRepository,
    FakeUnitOfWork,
)


class MemoryRequirementFileRepository:
    def __init__(self) -> None:
        self.items: list[RequirementFile] = []

    async def list_by_project(self, project_id: UUID) -> list[RequirementFile]:
        return [item for item in self.items if item.project_id == project_id]

    async def get_by_id(self, file_id: UUID) -> RequirementFile | None:
        return next((item for item in self.items if item.id == file_id), None)

    async def save(self, entity: RequirementFile) -> RequirementFile:
        self.items = [item for item in self.items if item.id != entity.id]
        self.items.append(entity)
        return entity

    async def delete(self, file_id: UUID) -> bool:
        before = len(self.items)
        self.items = [item for item in self.items if item.id != file_id]
        return len(self.items) != before


class MemoryFileStore:
    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}

    async def save_file(self, project_id: str, filename: str, content: bytes) -> str:
        location = f"{project_id}/{filename}"
        self.files[location] = content
        return location

    async def read_file(self, file_path: str) -> bytes:
        return self.files[file_path]

    async def delete_file(self, file_path: str) -> None:
        self.files.pop(file_path, None)

    async def cleanup_empty_dir(self, project_id: str) -> None:
        del project_id


class FailingUnitOfWork(FakeUnitOfWork):
    async def commit(self) -> None:
        raise RuntimeError("database commit failed")


def _service(
    project: Project,
    repository: MemoryRequirementFileRepository,
    storage: MemoryFileStore,
    unit_of_work: FakeUnitOfWork | None = None,
) -> RequirementFileService:
    projects = FakeProjectRepository([project])
    members = FakeProjectMemberRepository([])
    return RequirementFileService(
        repository,
        storage,
        RequirementDocumentParser(),
        projects,
        unit_of_work or FakeUnitOfWork(),
        ProjectAccessPolicy(projects, members, project.user_id),
    )


@pytest.mark.asyncio
async def test_upload_replace_without_context_change_then_delete() -> None:
    project = Project(name="Revenue", user_id=uuid4())
    repository = MemoryRequirementFileRepository()
    storage = MemoryFileStore()
    service = _service(project, repository, storage)

    first = await service.upload_files(
        UploadRequirementFilesInput(
            project.id, (RequirementUploadInput("brief.md", b"# Revenue"),), 0
        )
    )
    same = await service.upload_files(
        UploadRequirementFilesInput(
            project.id, (RequirementUploadInput("brief.md", b"# Revenue"),), 1
        )
    )
    changed = await service.upload_files(
        UploadRequirementFilesInput(
            project.id, (RequirementUploadInput("brief.md", b"# Net revenue"),), 1
        )
    )
    await service.delete_file(
        DeleteRequirementFileInput(project.id, changed.items[0].id, 2)
    )

    assert first.requirement_revision == same.requirement_revision == 1
    assert changed.requirement_revision == 2
    assert repository.items == []
    assert storage.files == {}
    assert project.requirement_revision == 3


@pytest.mark.asyncio
async def test_upload_compensates_storage_when_transaction_fails() -> None:
    project = Project(name="Revenue", user_id=uuid4())
    repository = MemoryRequirementFileRepository()
    storage = MemoryFileStore()
    service = _service(project, repository, storage, FailingUnitOfWork())

    with pytest.raises(RuntimeError, match="database commit failed"):
        await service.upload_files(
            UploadRequirementFilesInput(
                project.id, (RequirementUploadInput("brief.txt", b"Revenue"),), 0
            )
        )

    assert storage.files == {}
