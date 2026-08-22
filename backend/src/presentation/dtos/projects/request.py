"""Request DTO và path constraints cho Project API."""

from typing import Annotated
from uuid import UUID

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field
from src.application.projects.input import CreateProjectInput, UpdateProjectInput
from src.domain.project.project_details_rules import (
    MAX_PROJECT_DOMAIN_LENGTH,
    MAX_PROJECT_NAME_LENGTH,
    MIN_PROJECT_NAME_LENGTH,
    MIN_PROJECT_REQUIREMENT_LENGTH,
)

ProjectIdPath = Annotated[UUID, Path(description="ID của Project")]


class ProjectMutationRequest(BaseModel):
    """Các trường Project dùng chung giữa create và full update."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=MIN_PROJECT_NAME_LENGTH,
        max_length=MAX_PROJECT_NAME_LENGTH,
        description="Tên Project",
    )
    requirement: str | None = Field(
        default=None,
        min_length=MIN_PROJECT_REQUIREMENT_LENGTH,
        description="Yêu cầu nghiệp vụ thô, có thể bổ sung sau khi tạo Project",
    )
    domain: str | None = Field(
        default=None,
        max_length=MAX_PROJECT_DOMAIN_LENGTH,
        description="Lĩnh vực nghiệp vụ",
    )
    description: str | None = Field(default=None, description="Mô tả Project")


class CreateProjectRequest(ProjectMutationRequest):
    """Payload tạo Project mới."""

    def to_application(self) -> CreateProjectInput:
        """Ánh xạ create request sang application input."""
        return CreateProjectInput(
            name=self.name,
            requirement=self.requirement,
            domain=self.domain,
            description=self.description,
        )


class UpdateProjectRequest(ProjectMutationRequest):
    """Payload thay thế thông tin thuộc Project."""

    def to_application(self, project_id: UUID) -> UpdateProjectInput:
        """Ánh xạ update request sang application input."""
        return UpdateProjectInput(
            project_id=project_id,
            name=self.name,
            requirement=self.requirement,
            domain=self.domain,
            description=self.description,
        )
