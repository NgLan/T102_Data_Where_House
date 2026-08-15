"""Pydantic Response Schemas cho nhóm endpoint Mô hình Dữ liệu (Data Models)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.domain.data_model.enums import SqlDialect


class DataModelResponse(BaseModel):
    """Mô hình dữ liệu hiện hành của một dự án."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Định danh mô hình dữ liệu")
    project_id: UUID = Field(description="Định danh dự án sở hữu mô hình dữ liệu")
    dbml: str = Field(description="Nội dung DBML chính thức đang lưu trong hệ thống")
    revision: int = Field(description="Số hiệu phiên bản hiện tại của mô hình dữ liệu")
    created_at: datetime = Field(description="Thời điểm khởi tạo")
    updated_at: datetime = Field(description="Thời điểm cập nhật gần nhất")


class DdlGenerationResponse(BaseModel):
    """Script DDL sinh từ mô hình dữ liệu theo hệ quản trị CSDL đã chọn."""

    model_config = ConfigDict(from_attributes=True)

    data_model_id: UUID = Field(description="Định danh mô hình dữ liệu nguồn")
    revision: int = Field(description="Revision của mô hình dữ liệu tại thời điểm sinh mã")
    dialect: SqlDialect = Field(description="Hệ quản trị CSDL đích của script DDL")
    schema_name: str = Field(description="Tên schema Sandbox được gắn vào mọi bảng")
    ddl: str = Field(description="Nội dung script DDL hoàn chỉnh")
    table_count: int = Field(description="Số bảng được sinh trong script")
    warnings: list[str] = Field(
        default_factory=list,
        description="Danh sách cảnh báo tương thích khi chuyển đổi sang dialect đích",
    )
