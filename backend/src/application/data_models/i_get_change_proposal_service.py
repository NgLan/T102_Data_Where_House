"""Interface Use Case: Xem chi tiết đề xuất thay đổi mô hình dữ liệu (UC6.1)."""

from abc import ABC, abstractmethod

from src.application.data_models.dto import (
    ChangeProposalDetailOutput,
    GetChangeProposalInput,
)


class IGetChangeProposalService(ABC):
    """Interface trừu tượng cho use case xem chi tiết một đề xuất thay đổi."""

    @abstractmethod
    async def execute(self, payload: GetChangeProposalInput) -> ChangeProposalDetailOutput:
        """Trả về nội dung đề xuất kèm DBML hiện hành để đối chiếu khác biệt."""
        pass
