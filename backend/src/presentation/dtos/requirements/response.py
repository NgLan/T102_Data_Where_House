"""Response schemas cho API Requirement."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.requirements.output import RequirementOutput
from src.domain.requirement.enums import RequirementPriority, RequirementType


class RequirementResponse(BaseModel):
    """Yêu cầu nghiệp vụ trả về cho Frontend."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="ID của yêu cầu")
    project_id: UUID = Field(description="ID dự án sở hữu yêu cầu")
    title: str = Field(description="Tiêu đề yêu cầu")
    description: str = Field(description="Mô tả nghiệp vụ chi tiết")
    type: RequirementType = Field(description="Phân loại yêu cầu")
    priority: RequirementPriority = Field(description="Mức độ ưu tiên")
    created_at: datetime = Field(description="Thời điểm tạo theo ISO 8601")
    updated_at: datetime = Field(description="Thời điểm cập nhật theo ISO 8601")

    @classmethod
    def from_application(cls, output: RequirementOutput) -> "RequirementResponse":
        """Ánh xạ application output sang response DTO."""
        return cls.model_validate(output)
