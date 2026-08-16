"""Interface duy nhất cho các thao tác application Data Model."""

from abc import ABC, abstractmethod

from src.application.data_models.input import (
    GenerateDataModelInput,
    GetDataModelInput,
    UpdateDataModelInput,
)
from src.application.data_models.output import (
    DataModelDdlOutput,
    DataModelInsightOutput,
    DataModelOutput,
)


class IDataModelService(ABC):
    """Hợp đồng công khai của application service Data Model."""

    @abstractmethod
    async def get_data_model(self, data: GetDataModelInput) -> DataModelOutput:
        """Lấy Data Model hiện tại của dự án."""
        raise NotImplementedError

    @abstractmethod
    async def update_data_model(self, data: UpdateDataModelInput) -> DataModelOutput:
        """Cập nhật Data Model bằng optimistic locking."""
        raise NotImplementedError

    @abstractmethod
    async def generate_data_model(self, data: GenerateDataModelInput) -> DataModelOutput:
        """Chạy pipeline AI sinh Data Model từ yêu cầu và nguồn dữ liệu của dự án."""
        raise NotImplementedError
        
    @abstractmethod
    async def generate_ddl(self, data: GetDataModelInput, dialect: str) -> DataModelDdlOutput:
        """Sinh DDL từ snapshot hiện tại."""
        raise NotImplementedError

    @abstractmethod
    async def get_insights(self, data: GetDataModelInput) -> list[DataModelInsightOutput]:
        """Lấy insight được phân tích từ snapshot hiện tại."""
        raise NotImplementedError
