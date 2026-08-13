"""Giao diện Repository cho miền Mô hình Dữ liệu (Data Model)."""

from abc import abstractmethod

from src.domain.data_model.entities import DataModel, DataModelChange
from src.domain.shared.repository import IBaseRepository
from src.domain.shared.types import EntityID


class IDataModelRepository(IBaseRepository[DataModel]):
    """Interface trừu tượng cho thao tác lưu trữ và truy vấn thực thể DataModel."""

    @abstractmethod
    async def get_by_project_id(self, project_id: EntityID) -> DataModel | None:
        """Lấy mô hình dữ liệu theo dự án."""
        pass


class IDataModelChangeRepository(IBaseRepository[DataModelChange]):
    """Interface trừu tượng cho thao tác lưu trữ đề xuất thay đổi mô hình dữ liệu."""

    @abstractmethod
    async def list_by_data_model(self, data_model_id: EntityID) -> list[DataModelChange]:
        """Danh sách các đề xuất thay đổi thuộc một mô hình dữ liệu."""
        pass
