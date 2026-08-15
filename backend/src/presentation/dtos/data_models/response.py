"""Response schemas cho API Data Model."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.data_models.output import DataModelOutput


class DataModelResponse(BaseModel):
    """Snapshot Data Model trả về cho Frontend editor."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="ID của Data Model")
    project_id: UUID = Field(description="ID dự án sở hữu Data Model")
    dbml: str = Field(min_length=1, description="Snapshot DBML hiện tại")
    revision: int = Field(ge=1, description="Revision phục vụ optimistic locking")
    created_at: datetime = Field(description="Thời điểm tạo theo ISO 8601")
    updated_at: datetime = Field(description="Thời điểm cập nhật theo ISO 8601")

    @classmethod
    def from_application(cls, output: DataModelOutput) -> "DataModelResponse":
        """Ánh xạ application output sang response DTO."""
        return cls.model_validate(output)
