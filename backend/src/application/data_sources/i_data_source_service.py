"""Interface duy nhất của module Data Source."""

from abc import ABC, abstractmethod

from src.application.data_sources.input import (
    DataSourceIdInput,
    ListDataSourcesInput,
    UpdateDataSourceColumnInput,
    UploadDataSourcesInput,
)
from src.application.data_sources.output import (
    DataSourceListOutput,
    DataSourceOutput,
    PreviewOutput,
    UploadDataSourcesOutput,
)


class IDataSourceService(ABC):
    """Hợp đồng application cho toàn bộ use case Data Source."""

    @abstractmethod
    async def list_data_sources(self, data: ListDataSourcesInput) -> DataSourceListOutput:
        """Liệt kê nguồn nếu actor là thành viên dự án."""
        raise NotImplementedError

    @abstractmethod
    async def upload_data_sources(self, data: UploadDataSourcesInput) -> UploadDataSourcesOutput:
        """Upload CSV/DOCX nếu actor là OWNER."""
        raise NotImplementedError

    @abstractmethod
    async def get_preview(self, data: DataSourceIdInput) -> PreviewOutput:
        """Đọc preview nếu actor là thành viên dự án."""
        raise NotImplementedError

    @abstractmethod
    async def update_column(self, data: UpdateDataSourceColumnInput) -> DataSourceOutput:
        """Cập nhật metadata cột nếu actor là OWNER."""
        raise NotImplementedError

    @abstractmethod
    async def delete_data_source(self, data: DataSourceIdInput) -> None:
        """Xóa nguồn nếu actor là OWNER."""
        raise NotImplementedError
