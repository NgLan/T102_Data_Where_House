"""Data Transfer Objects (DTO) cho miền Mô hình Dữ liệu (Data Model)."""

from datetime import datetime
from src.domain.data_model.enums import DataModelChangeStatus
from src.domain.shared.types import EntityID
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Giới hạn độ dài câu lệnh chỉnh sửa bằng ngôn ngữ tự nhiên người dùng gửi cho AI Agent.
MIN_INSTRUCTION_LENGTH = 5
MAX_INSTRUCTION_LENGTH = 2000


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


class AcceptChangeProposalInput(BaseModel):
    """Tham số chấp nhận và áp dụng một đề xuất thay đổi vào mô hình dữ liệu."""

    model_config = ConfigDict(frozen=True)

    change_id: EntityID = Field(description="Định danh đề xuất thay đổi cần chấp nhận")


class RejectChangeProposalInput(BaseModel):
    """Tham số từ chối một đề xuất thay đổi."""

    model_config = ConfigDict(frozen=True)

    change_id: EntityID = Field(description="Định danh đề xuất thay đổi cần từ chối")


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
    summary: str = Field(
        default="",
        description=(
            "Lời giải thích của AI Agent về thay đổi vừa đề xuất. Chỉ có giá trị ngay sau khi "
            "tạo đề xuất (T-024); khi truy vấn lại đề xuất đã lưu thì trường này rỗng vì "
            "nội dung diễn giải không được lưu xuống CSDL."
        ),
    )
    created_at: datetime
    updated_at: datetime


class ReviseDataModelInput(BaseModel):
    """Tham số yêu cầu AI chỉnh sửa mô hình dữ liệu bằng ngôn ngữ tự nhiên (T-024)."""

    model_config = ConfigDict(frozen=True)

    data_model_id: EntityID = Field(description="Định danh mô hình dữ liệu cần chỉnh sửa")
    instruction: str = Field(
        min_length=MIN_INSTRUCTION_LENGTH,
        max_length=MAX_INSTRUCTION_LENGTH,
        description="Yêu cầu chỉnh sửa bằng ngôn ngữ tự nhiên",
    )


class AcceptChangeProposalInput(BaseModel):
    """Tham số chấp nhận và áp dụng một đề xuất thay đổi vào mô hình dữ liệu (T-032)."""

    model_config = ConfigDict(frozen=True)

    change_id: EntityID = Field(description="Định danh đề xuất thay đổi cần chấp nhận")


class RejectChangeProposalInput(BaseModel):
    """Tham số từ chối một đề xuất thay đổi (T-033)."""

    model_config = ConfigDict(frozen=True)

    change_id: EntityID = Field(description="Định danh đề xuất thay đổi cần từ chối")
