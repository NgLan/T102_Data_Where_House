"""Interface Use Case: Tạo đề xuất thay đổi mô hình dữ liệu bằng AI (T-024 / FR5.2)."""

from abc import ABC, abstractmethod

from src.application.data_models.dto import (
    ChangeProposalDetailOutput,
    ReviseDataModelInput,
)


class ICreateChangeProposalService(ABC):
    """Interface trừu tượng cho use case nhờ AI chỉnh sửa mô hình dữ liệu."""

    @abstractmethod
    async def execute(self, payload: ReviseDataModelInput) -> ChangeProposalDetailOutput:
        """Sinh đề xuất DBML mới bằng AI và lưu lại ở trạng thái PROPOSED."""
        pass
