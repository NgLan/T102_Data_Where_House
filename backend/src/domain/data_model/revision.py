"""Cổng (Port) chỉnh sửa mô hình dữ liệu bằng AI thuộc miền Mô hình Dữ liệu (UC6 / T-024)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DbmlRevisionProposal:
    """Kết quả một lượt chỉnh sửa DBML do AI Agent đề xuất."""

    dbml: str
    summary: str
    changed_tables: list[str] = field(default_factory=list)
    attempts: int = 1


class IDataModelReviser(ABC):
    """Interface trừu tượng cho bộ chỉnh sửa mô hình dữ liệu bằng ngôn ngữ tự nhiên.

    Tầng Application chỉ phụ thuộc vào interface này, không biết gì về LangGraph hay
    nhà cung cấp LLM cụ thể đang được dùng ở tầng Infrastructure.
    """

    @abstractmethod
    async def revise(self, current_dbml: str, instruction: str) -> DbmlRevisionProposal:
        """Sinh phiên bản DBML mới từ DBML hiện tại và yêu cầu bằng ngôn ngữ tự nhiên."""
        pass
