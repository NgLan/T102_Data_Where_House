"""Request schemas và parameter constraints cho API Requirement."""

from typing import Annotated
from uuid import UUID

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field
from src.application.requirements.input import CreateRequirementInput
from src.domain.requirement.enums import RequirementPriority, RequirementType

MAX_TITLE_LENGTH = 255
MAX_DESCRIPTION_LENGTH = 15_000

ProjectIdPath = Annotated[UUID, Path(description="ID dự án chứa yêu cầu")]


class CreateRequirementRequest(BaseModel):
    """Payload tạo mới một yêu cầu nghiệp vụ thô."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=1,
        max_length=MAX_TITLE_LENGTH,
        description="Tiêu đề ngắn gọn của yêu cầu",
    )
    description: str = Field(
        min_length=1,
        max_length=MAX_DESCRIPTION_LENGTH,
        description="Mô tả nghiệp vụ chi tiết, viết bằng ngôn ngữ tự nhiên",
    )
    type: RequirementType = Field(
        default=RequirementType.BUSINESS,
        description="Phân loại yêu cầu",
    )
    priority: RequirementPriority = Field(
        default=RequirementPriority.MEDIUM,
        description="Mức độ ưu tiên",
    )

    def to_application(self, project_id: UUID) -> CreateRequirementInput:
        """Ánh xạ request DTO sang application input."""
        return CreateRequirementInput(
            project_id=project_id,
            title=self.title,
            description=self.description,
            type=self.type,
            priority=self.priority,
        )
