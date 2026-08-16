"""Outbound port lưu trữ file của Data Source."""

from typing import Protocol


class IDataSourceFileStore(Protocol):
    """Hợp đồng storage do application layer sở hữu."""

    async def save_file(self, project_id: str, filename: str, content: bytes) -> str:
        """Lưu file và trả về location nội bộ."""
        ...

    async def read_file(self, file_path: str) -> bytes:
        """Đọc nội dung file theo location nội bộ."""
        ...

    async def delete_file(self, file_path: str) -> None:
        """Xóa file theo location nội bộ."""
        ...

    async def cleanup_empty_dir(self, project_id: str) -> None:
        """Xóa thư mục dự án khi đã rỗng."""
        ...
