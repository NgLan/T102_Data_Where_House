"""Interface Use Case: Lấy mô hình dữ liệu hiện hành của một dự án."""

from abc import ABC, abstractmethod

from src.application.data_models.dto import DataModelOutput, GetDataModelInput


class IGetDataModelService(ABC):
    """Interface trừu tượng cho use case truy vấn mô hình dữ liệu theo dự án."""

    @abstractmethod
    async def execute(self, payload: GetDataModelInput) -> DataModelOutput:
        """Trả về mô hình dữ liệu hiện hành của dự án."""
        pass
