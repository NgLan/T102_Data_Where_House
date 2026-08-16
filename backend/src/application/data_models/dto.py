"""Data Transfer Objects (DTO) cho miền Mô hình Dữ liệu (Data Model)."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UpdateDataModelCommand(BaseModel):
    """Lệnh cập nhật nội dung DBML cho Data Model của dự án."""

    model_config = ConfigDict(frozen=True)

    project_id: UUID = Field(..., description="ID của dự án")
    dbml: str = Field(..., description="Nội dung mã DBML mới")
    expected_revision: int | None = Field(
        default=None, description="Revision kỳ vọng phục vụ kiểm tra xung đột"
    )


class DataModelDto(BaseModel):
    """DTO biểu diễn thông tin Mô hình Dữ liệu (Data Model) trả về cho client."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID của Data Model")
    project_id: UUID = Field(..., description="ID của dự án liên kết")
    dbml: str = Field(..., description="Mã nguồn DBML hiện tại")
    revision: int = Field(..., description="Số hiệu phiên bản (revision)")
    created_at: str = Field(..., description="Thời điểm khởi tạo (ISO 8601 UTC)")
    updated_at: str = Field(..., description="Thời điểm cập nhật gần nhất (ISO 8601 UTC)")
