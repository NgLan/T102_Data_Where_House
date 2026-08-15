"""Interface Use Case: Liệt kê đề xuất thay đổi của một mô hình dữ liệu (UC6.1)."""

from abc import ABC, abstractmethod

from src.application.data_models.dto import (
    ChangeProposalSummaryOutput,
    ListChangeProposalsInput,
)


class IListChangeProposalsService(ABC):
    """Interface trừu tượng cho use case liệt kê đề xuất thay đổi mô hình dữ liệu."""

    @abstractmethod
    async def execute(
        self, payload: ListChangeProposalsInput
    ) -> list[ChangeProposalSummaryOutput]:
        """Trả về danh sách đề xuất thay đổi, mới nhất trước."""
        pass
