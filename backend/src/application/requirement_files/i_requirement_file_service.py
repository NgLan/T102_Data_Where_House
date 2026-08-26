"""Service contract và outbound ports của Requirement Documents."""

from abc import ABC, abstractmethod
from typing import Protocol

from src.application.common.i_file_store import IFileStore
from src.application.requirement_files.input import (
    DeleteRequirementFileInput,
    ListRequirementFilesInput,
    UploadRequirementFilesInput,
)
from src.application.requirement_files.output import (
    RequirementFileListOutput,
    UploadRequirementFilesOutput,
)
from src.domain.requirement_file.enums import RequirementFileType


class IRequirementFileStore(IFileStore, Protocol):
    """Storage port cho Requirement Documents."""

    pass


class IRequirementDocumentParser(Protocol):
    """Parser port không leak thư viện DOCX qua application boundary."""

    def parse(
        self, filename: str, content: bytes
    ) -> tuple[RequirementFileType, str]: ...


class IRequirementFileService(ABC):
    @abstractmethod
    async def list_files(
        self, data: ListRequirementFilesInput
    ) -> RequirementFileListOutput: ...

    @abstractmethod
    async def upload_files(
        self, data: UploadRequirementFilesInput
    ) -> UploadRequirementFilesOutput: ...

    @abstractmethod
    async def delete_file(self, data: DeleteRequirementFileInput) -> None: ...
