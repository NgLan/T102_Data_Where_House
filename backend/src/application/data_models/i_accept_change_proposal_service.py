"""Interface Use Case: Chấp nhận đề xuất thay đổi mô hình dữ liệu (UC6.2 / T-032)."""

from abc import ABC, abstractmethod

from src.application.data_models.dto import AcceptChangeProposalInput, DataModelOutput


class IAcceptChangeProposalService(ABC):
    """Interface trừu tượng cho use case chấp nhận và áp dụng đề xuất thay đổi."""

    @abstractmethod
    async def execute(self, payload: AcceptChangeProposalInput) -> DataModelOutput:
        """Áp dụng đề xuất vào mô hình dữ liệu và trả về mô hình sau khi cập nhật."""
        pass
