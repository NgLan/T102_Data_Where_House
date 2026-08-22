"""Response DTO cho đề xuất thay đổi Data Model."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.data_models.output import ChangeProposalDetailOutput
from src.domain.data_model.enums import DataModelChangeStatus


class ChangeProposalSummaryResponse(BaseModel):
    """Thông tin tóm tắt một đề xuất thay đổi."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="Định danh đề xuất thay đổi")
    data_model_id: UUID = Field(description="Định danh Data Model liên quan")
    user_id: UUID = Field(description="Định danh người tạo đề xuất")
    base_revision: int = Field(description="Revision Data Model khi tạo đề xuất")
    status: DataModelChangeStatus = Field(description="Trạng thái đề xuất")
    created_at: datetime = Field(description="Thời điểm khởi tạo")
    updated_at: datetime = Field(description="Thời điểm cập nhật gần nhất")


class ChangeProposalDetailResponse(ChangeProposalSummaryResponse):
    """Chi tiết proposal kèm snapshot hiện hành."""

    proposed_dbml: str = Field(description="DBML do Agent đề xuất")
    current_dbml: str = Field(description="DBML chính thức đang áp dụng")
    current_revision: int = Field(description="Revision hiện tại của Data Model")
    is_outdated: bool = Field(description="Proposal không còn khớp revision hiện tại")

    @classmethod
    def from_application(
        cls,
        output: ChangeProposalDetailOutput,
    ) -> "ChangeProposalDetailResponse":
        """Làm phẳng application output thành response payload."""
        summary = output.summary
        return cls(
            id=summary.id,
            data_model_id=summary.data_model_id,
            user_id=summary.user_id,
            base_revision=summary.base_revision,
            status=summary.status,
            created_at=summary.created_at,
            updated_at=summary.updated_at,
            proposed_dbml=output.proposed_dbml,
            current_dbml=output.current_dbml,
            current_revision=output.current_revision,
            is_outdated=output.is_outdated,
        )
