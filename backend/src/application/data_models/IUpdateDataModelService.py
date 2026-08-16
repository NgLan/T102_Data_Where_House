"""Interface định nghĩa Use Case Cập nhật Mã DBML Mô hình Dữ liệu."""

from abc import ABC, abstractmethod

from src.application.data_models.dto import DataModelDto, UpdateDataModelCommand


class IUpdateDataModelService(ABC):
    """Interface trừu tượng cho usecase cập nhật mã DBML (UC5.1.1)."""

    @abstractmethod
    async def execute(self, command: UpdateDataModelCommand) -> DataModelDto:
        """Thực thi cập nhật hoặc tạo mới DBML cho dự án.

        Args:
            command: Lệnh cập nhật DBML kèm project_id và expected_revision.

        Returns:
            DataModelDto: Dữ liệu mô hình đã được cập nhật và tăng revision.
        """
        pass
