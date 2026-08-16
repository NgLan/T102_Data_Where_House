"""Interface cho tầng lưu trữ tệp tin (File Storage)."""

from abc import ABC, abstractmethod


class IFileStorage(ABC):
    """Interface định nghĩa các thao tác lưu trữ tệp tin vật lý."""

    @abstractmethod
    async def save_file(self, project_id: str, filename: str, content: bytes) -> str:
        """Lưu tệp tin và trả về đường dẫn đã lưu.

        Args:
            project_id: ID của dự án sở hữu tệp.
            filename: Tên tệp tin.
            content: Nội dung nhị phân của tệp.

        Returns:
            str: Đường dẫn lưu trữ tệp.
        """
        pass

    @abstractmethod
    async def read_file(self, file_path: str) -> bytes:
        """Đọc nội dung tệp tin từ đường dẫn lưu trữ.

        Args:
            file_path: Đường dẫn tệp tin.

        Returns:
            bytes: Nội dung nhị phân của tệp.
        """
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> None:
        """Xóa tệp tin vật lý.

        Args:
            file_path: Đường dẫn tệp tin cần xóa.
        """
        pass

    @abstractmethod
    async def delete_directory(self, dir_path: str) -> None:
        """Xóa đệ quy toàn bộ thư mục và tệp tin bên trong.

        Args:
            dir_path: Đường dẫn thư mục cần xóa.
        """
        pass

    @abstractmethod
    async def cleanup_empty_dir(self, project_id: str) -> None:
        """Dọn dẹp thư mục dự án nếu rỗng (không còn tệp tin nào).

        Args:
            project_id: ID của dự án cần kiểm tra và dọn dẹp.
        """
        pass

