"""Interface duy nhất của module Data Source."""

from abc import ABC, abstractmethod
from typing import Protocol

from src.application.data_sources.input import (
    DataSourceIdInput,
    DataSourcePreviewInput,
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


class IDataSourceFileStore(Protocol):
    """Outbound port lưu trữ file nguồn."""

    async def save_file(self, project_id: str, filename: str, content: bytes) -> str: ...

    async def read_file(self, file_path: str) -> bytes: ...

    async def delete_file(self, file_path: str) -> None: ...

    async def cleanup_empty_dir(self, project_id: str) -> None: ...


class IDataSourceService(ABC):
    """Hợp đồng application cho toàn bộ use case Data Source."""

    @abstractmethod
    async def list_data_sources(self, data: ListDataSourcesInput) -> DataSourceListOutput:
        """Liệt kê nguồn nếu actor là thành viên dự án.

        Args:
            data: Project cần đọc nguồn.
        Returns:
            Danh sách nguồn và quyền chỉnh sửa.
        Raises:
            BusinessException: Khi actor không phải thành viên.
            InfrastructureException: Khi persistence thất bại.
        """
        raise NotImplementedError

    @abstractmethod
    async def upload_data_sources(self, data: UploadDataSourcesInput) -> UploadDataSourcesOutput:
        """Upload file CSV nếu actor là OWNER.

        Args:
            data: Batch file CSV và Project đích.
        Returns:
            Danh sách nguồn dữ liệu đã lưu và số lượng file đã xử lý.
        Raises:
            BusinessException: Khi không phải OWNER hoặc upload vi phạm policy.
            InfrastructureException: Khi parser, storage hoặc persistence thất bại.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_preview(self, data: DataSourcePreviewInput) -> PreviewOutput:
        """Đọc preview nếu actor là thành viên dự án.

        Args:
            data: Project và nguồn cần xem.
        Returns:
            Các dòng preview cùng tổng số dòng.
        Raises:
            BusinessException: Khi nguồn không tồn tại hoặc actor không phải thành viên.
            InfrastructureException: Khi parser, storage hoặc persistence thất bại.
        """
        raise NotImplementedError

    @abstractmethod
    async def update_column(self, data: UpdateDataSourceColumnInput) -> DataSourceOutput:
        """Cập nhật metadata cột nếu actor là OWNER.

        Args:
            data: Định danh cột và metadata mới.
        Returns:
            Nguồn sau khi cập nhật.
        Raises:
            BusinessException: Khi không phải OWNER, nguồn hoặc cột không tồn tại.
            InfrastructureException: Khi persistence thất bại.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_data_source(self, data: DataSourceIdInput) -> None:
        """Xóa nguồn nếu actor là OWNER.

        Args:
            data: Project và nguồn cần xóa.
        Returns:
            Không có giá trị trả về.
        Raises:
            BusinessException: Khi không phải OWNER hoặc nguồn không tồn tại.
            InfrastructureException: Khi storage hoặc persistence thất bại.
        """
        raise NotImplementedError
