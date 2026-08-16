"""Interface định nghĩa Use Case Lấy Mô hình Dữ liệu của Dự án."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.application.data_models.dto import DataModelDto


class IGetDataModelService(ABC):
    """Interface trừu tượng cho usecase lấy DataModel hiện tại của dự án."""

    @abstractmethod
    async def execute(self, project_id: UUID) -> DataModelDto | None:
        """Lấy thông tin mô hình dữ liệu theo ID dự án.

        Args:
            project_id: UUID của dự án cần tra cứu.

        Returns:
            DataModelDto | None: Thông tin mô hình nếu đã tồn tại, hoặc None.
        """
        pass
