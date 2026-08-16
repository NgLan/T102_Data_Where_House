"""Interface Use Case: Từ chối đề xuất thay đổi mô hình dữ liệu (UC6.3 / T-033)."""

from abc import ABC, abstractmethod

from src.application.data_models.dto import (
    ChangeProposalSummaryOutput,
    RejectChangeProposalInput,
)


class IRejectChangeProposalService(ABC):
    """Interface trừu tượng cho use case từ chối một đề xuất thay đổi."""

    @abstractmethod
    async def execute(
        self, payload: RejectChangeProposalInput
    ) -> ChangeProposalSummaryOutput:
        """Đánh dấu đề xuất là REJECTED và trả về thông tin tóm tắt sau khi cập nhật."""
        pass
