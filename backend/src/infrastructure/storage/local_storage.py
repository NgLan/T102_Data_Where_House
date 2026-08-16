"""Triển khai lưu trữ tệp tin cục bộ (Local File Storage)."""

import os
import re
import shutil
from pathlib import Path

import anyio
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.storage.file_storage import IFileStorage

DEFAULT_UPLOAD_DIR = Path("data/uploads")


class LocalFileStorage(IFileStorage):
    """Lưu trữ tệp tin trên hệ thống tệp cục bộ của server."""

    def __init__(self, base_dir: Path = DEFAULT_UPLOAD_DIR) -> None:
        """Khởi tạo storage với thư mục gốc.

        Args:
            base_dir: Thư mục lưu trữ gốc.
        """
        self.base_dir = base_dir.resolve()

    def _sanitize_filename(self, filename: str) -> str:
        """Chuẩn hóa tên tệp loại bỏ ký tự nguy hiểm và chống path traversal."""
        if ".." in filename:
            raise InfrastructureException(
                code=ErrorCode.STORAGE_ERROR,
                message=f"Phát hiện truy cập đường dẫn không hợp lệ trong tên tệp: {filename}",
            )
        base_name = os.path.basename(filename)
        cleaned = re.sub(r"[^\w\.\-\_]", "_", base_name)
        return cleaned or "unnamed_file"

    def _resolve_and_validate_path(self, target_input: str | Path) -> Path:
        """Giải quyết và kiểm tra an toàn đường dẫn tệp tin trong base_dir."""
        norm_str = str(target_input).replace("\\", "/").strip()
        if ".." in norm_str:
            raise InfrastructureException(
                code=ErrorCode.STORAGE_ERROR,
                message=f"Phát hiện truy cập đường dẫn không hợp lệ: {target_input}",
            )

        target = self._normalize_target_path(norm_str, target_input)
        resolved = target.resolve()
        base_str = str(self.base_dir).lower()
        resolved_str = str(resolved).lower()

        if not resolved_str.startswith(base_str):
            raise InfrastructureException(
                code=ErrorCode.STORAGE_ERROR,
                message=f"Phát hiện truy cập đường dẫn không hợp lệ: {target_input}",
            )
        return resolved

    def _normalize_target_path(self, norm_str: str, original_input: str | Path) -> Path:
        """Chuẩn hóa đường dẫn đích loại bỏ các tiền tố thư mục lưu trữ nếu có."""
        target = Path(original_input)
        if target.is_absolute():
            return target
        if norm_str.startswith("data/uploads/"):
            return self.base_dir / norm_str[len("data/uploads/") :]
        if norm_str.startswith("uploads/"):
            return self.base_dir / norm_str[len("uploads/") :]
        return self.base_dir / target

    async def save_file(self, project_id: str, filename: str, content: bytes) -> str:
        """Lưu tệp tin an toàn vào thư mục của project."""
        try:
            safe_name = self._sanitize_filename(filename)
            target_dir = self._resolve_and_validate_path(project_id)
            target_dir.mkdir(parents=True, exist_ok=True)
            file_path = self._resolve_and_validate_path(target_dir / safe_name)
            await anyio.Path(file_path).write_bytes(content)
            return str(file_path.as_posix())
        except InfrastructureException:
            raise
        except Exception as exc:
            raise InfrastructureException(
                code=ErrorCode.STORAGE_ERROR,
                message=f"Lỗi khi lưu tệp tin cục bộ: {filename}",
            ) from exc

    async def read_file(self, file_path: str) -> bytes:
        """Đọc nội dung tệp tin từ đường dẫn an toàn."""
        try:
            path = self._resolve_and_validate_path(file_path)
            return await anyio.Path(path).read_bytes()
        except InfrastructureException:
            raise
        except Exception as exc:
            raise InfrastructureException(
                code=ErrorCode.STORAGE_ERROR,
                message=f"Lỗi khi đọc tệp tin cục bộ: {file_path}",
            ) from exc

    async def delete_file(self, file_path: str) -> None:
        """Xóa tệp tin vật lý khỏi ổ đĩa."""
        try:
            path = self._resolve_and_validate_path(file_path)
            anyio_path = anyio.Path(path)
            if await anyio_path.exists():
                await anyio_path.unlink()
        except InfrastructureException:
            raise
        except Exception as exc:
            raise InfrastructureException(
                code=ErrorCode.STORAGE_ERROR,
                message=f"Lỗi khi xóa tệp tin cục bộ: {file_path}",
            ) from exc

    async def delete_directory(self, dir_path: str) -> None:
        """Xóa đệ quy toàn bộ thư mục và tệp tin bên trong."""
        try:
            path = self._resolve_and_validate_path(dir_path)
            if path.exists() and path.is_dir():
                shutil.rmtree(path)
        except InfrastructureException:
            raise
        except Exception as exc:
            raise InfrastructureException(
                code=ErrorCode.STORAGE_ERROR,
                message=f"Lỗi khi xóa thư mục: {dir_path}",
            ) from exc

    async def cleanup_empty_dir(self, project_id: str) -> None:
        """Dọn dẹp thư mục dự án nếu không còn tệp tin nào."""
        try:
            target_dir = self._resolve_and_validate_path(project_id)
            if target_dir.exists() and target_dir.is_dir():
                if not any(target_dir.iterdir()):
                    target_dir.rmdir()
        except InfrastructureException:
            raise
        except Exception as exc:
            raise InfrastructureException(
                code=ErrorCode.STORAGE_ERROR,
                message=f"Lỗi khi dọn dẹp thư mục dự án: {project_id}",
            ) from exc


