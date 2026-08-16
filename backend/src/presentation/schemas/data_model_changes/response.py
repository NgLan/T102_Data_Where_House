"""Pydantic Response Schemas cho nhóm endpoint Đề xuất Thay đổi Mô hình Dữ liệu."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.domain.data_model.enums import DataModelChangeStatus


class ChangeProposalSummaryResponse(BaseModel):
    """Thông tin tóm tắt một đề xuất thay đổi (dùng cho danh sách)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Định danh đề xuất thay đổi")
    data_model_id: UUID = Field(description="Định danh mô hình dữ liệu liên quan")
    user_id: UUID = Field(description="Định danh người tạo đề xuất")
    base_revision: int = Field(description="Revision của mô hình tại thời điểm tạo đề xuất")
    status: DataModelChangeStatus = Field(description="Trạng thái đề xuất")
    created_at: datetime = Field(description="Thời điểm khởi tạo")
    updated_at: datetime = Field(description="Thời điểm cập nhật gần nhất")


class ChangeProposalDetailResponse(ChangeProposalSummaryResponse):
    """Chi tiết đề xuất thay đổi kèm DBML hiện hành phục vụ khung so sánh khác biệt."""

    proposed_dbml: str = Field(description="Nội dung DBML do Agent/User đề xuất")
    current_dbml: str = Field(description="Nội dung DBML chính thức đang áp dụng")
    current_revision: int = Field(description="Revision hiện tại của mô hình dữ liệu")
    is_outdated: bool = Field(
        description=(
            "True khi base_revision không còn khớp revision hiện tại — "
            "đề xuất đã lỗi thời và sẽ gây xung đột nếu áp dụng"
        )
    )
    summary: str = Field(
        default="",
        description=(
            "Lời giải thích của AI Agent về thay đổi vừa đề xuất. Chỉ có nội dung ở phản hồi "
            "của endpoint tạo đề xuất bằng AI; khi truy vấn lại đề xuất đã lưu thì rỗng."
        ),
    )
