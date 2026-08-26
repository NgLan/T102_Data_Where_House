"""Public response payload không lộ location hoặc extracted text."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.requirement_files.output import (
    RequirementFileListOutput,
    RequirementFileOutput,
    UploadRequirementFilesOutput,
)
from src.domain.requirement_file.enums import RequirementFileType


class RequirementFileResponse(BaseModel):
    """Metadata an toàn của một Requirement Document."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="ID document")
    project_id: UUID = Field(description="ID Project")
    name: str = Field(description="Filename")
    file_type: RequirementFileType = Field(description="Định dạng document")
    created_at: datetime = Field(description="Thời điểm tạo")
    updated_at: datetime = Field(description="Thời điểm cập nhật")

    @classmethod
    def from_application(cls, output: RequirementFileOutput) -> "RequirementFileResponse":
        """Ánh xạ application output sang payload public."""
        return cls.model_validate(output)


class RequirementFileListResponse(BaseModel):
    """Danh sách document cùng quyền chỉnh sửa."""

    items: list[RequirementFileResponse]
    can_edit: bool

    @classmethod
    def from_application(
        cls, output: RequirementFileListOutput
    ) -> "RequirementFileListResponse":
        """Ánh xạ list output sang payload public."""
        return cls(
            items=[RequirementFileResponse.from_application(item) for item in output.items],
            can_edit=output.can_edit,
        )


class UploadRequirementFilesResponse(BaseModel):
    """Kết quả upload/replace một batch documents."""

    items: list[RequirementFileResponse]
    requirement_revision: int = Field(ge=0)

    @classmethod
    def from_application(
        cls, output: UploadRequirementFilesOutput
    ) -> "UploadRequirementFilesResponse":
        """Ánh xạ upload output sang payload public."""
        return cls(
            items=[RequirementFileResponse.from_application(item) for item in output.items],
            requirement_revision=output.requirement_revision,
        )
