"""DTO đầu vào/đầu ra cho các Use Case thuộc miền Mô hình Dữ liệu."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from src.domain.data_model.enums import DataModelChangeStatus, SqlDialect
from src.domain.shared.types import EntityID


class GetDataModelInput(BaseModel):
    """Tham số truy vấn mô hình dữ liệu của một dự án."""

    model_config = ConfigDict(frozen=True)

    project_id: EntityID = Field(description="Định danh dự án cần lấy mô hình dữ liệu")


class DataModelOutput(BaseModel):
    """Thông tin mô hình dữ liệu hiện hành của một dự án."""

    model_config = ConfigDict(frozen=True)

    id: EntityID
    project_id: EntityID
    dbml: str
    revision: int
    created_at: datetime
    updated_at: datetime


class GenerateDdlInput(BaseModel):
    """Tham số sinh mã DDL từ mô hình dữ liệu."""

    model_config = ConfigDict(frozen=True)

    data_model_id: EntityID = Field(description="Định danh mô hình dữ liệu cần sinh mã DDL")
    dialect: SqlDialect = Field(description="Hệ quản trị CSDL đích")
    schema_name: str | None = Field(
        default=None,
        description="Tên schema Sandbox tùy chọn, bỏ trống sẽ dùng schema mặc định",
    )


class GenerateDdlOutput(BaseModel):
    """Kết quả sinh mã DDL kèm cảnh báo tương thích dialect."""

    model_config = ConfigDict(frozen=True)

    data_model_id: EntityID
    revision: int
    dialect: SqlDialect
    schema_name: str
    ddl: str
    table_count: int
    warnings: list[str]


class ListChangeProposalsInput(BaseModel):
    """Tham số liệt kê đề xuất thay đổi của một mô hình dữ liệu."""

    model_config = ConfigDict(frozen=True)

    data_model_id: EntityID = Field(description="Định danh mô hình dữ liệu")
    status: DataModelChangeStatus | None = Field(
        default=None,
        description="Lọc theo trạng thái đề xuất, bỏ trống sẽ lấy tất cả",
    )


class ChangeProposalSummaryOutput(BaseModel):
    """Thông tin tóm tắt của một đề xuất thay đổi (dùng cho danh sách)."""

    model_config = ConfigDict(frozen=True)

    id: EntityID
    data_model_id: EntityID
    user_id: EntityID
    base_revision: int
    status: DataModelChangeStatus
    created_at: datetime
    updated_at: datetime


class GetChangeProposalInput(BaseModel):
    """Tham số truy vấn chi tiết một đề xuất thay đổi."""

    model_config = ConfigDict(frozen=True)

    change_id: EntityID = Field(description="Định danh đề xuất thay đổi cần xem")


class ChangeProposalDetailOutput(BaseModel):
    """Chi tiết đề xuất thay đổi kèm DBML hiện hành để đối chiếu khác biệt (UC6.1)."""

    model_config = ConfigDict(frozen=True)

    id: EntityID
    data_model_id: EntityID
    user_id: EntityID
    base_revision: int
    proposed_dbml: str
    status: DataModelChangeStatus
    current_dbml: str
    current_revision: int
    is_outdated: bool = Field(
        description="True khi base_revision không còn khớp revision hiện tại (nguy cơ xung đột)"
    )
    created_at: datetime
    updated_at: datetime
