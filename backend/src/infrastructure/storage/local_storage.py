"""Local filesystem adapter cho artifact của dự án."""

import re
import shutil
from pathlib import Path
from typing import NoReturn

import anyio
from src.application.data_sources.i_data_source_service import IDataSourceFileStore
from src.application.projects.i_project_service import IProjectArtifactStore
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.shared.types import EntityID
from typing_extensions import override


class LocalFileStorage(IDataSourceFileStore, IProjectArtifactStore):
    """Lưu file nguồn và artifact dự án dưới một thư mục gốc an toàn."""

    def __init__(self, base_dir: Path) -> None:
        """Khởi tạo adapter với upload root đã cấu hình."""
        self._base_dir = base_dir.resolve()

    @override
    async def save_file(self, project_id: str, filename: str, content: bytes) -> str:
        """Lưu file vào thư mục dự án và trả đường dẫn tuyệt đối."""
        try:
            directory = self._resolve(project_id)
            await anyio.Path(directory).mkdir(parents=True, exist_ok=True)
            path = self._resolve(Path(project_id) / self._safe_filename(filename))
            await anyio.Path(path).write_bytes(content)
            return path.as_posix()
        except InfrastructureException:
            raise
        except OSError as exc:
            self._raise_storage_error("Không thể lưu file nguồn.", exc)

    @override
    async def read_file(self, file_path: str) -> bytes:
        """Đọc file nằm trong upload root."""
        try:
            return await anyio.Path(self._resolve(file_path)).read_bytes()
        except InfrastructureException:
            raise
        except OSError as exc:
            self._raise_storage_error("Không thể đọc file nguồn.", exc)

    @override
    async def delete_file(self, file_path: str) -> None:
        """Xóa file nếu file còn tồn tại."""
        try:
            path = anyio.Path(self._resolve(file_path))
            if await path.exists():
                await path.unlink()
        except InfrastructureException:
            raise
        except OSError as exc:
            self._raise_storage_error("Không thể xóa file nguồn.", exc)

    @override
    async def cleanup_empty_dir(self, project_id: str) -> None:
        """Xóa thư mục dự án khi không còn artifact."""
        try:
            directory = self._resolve(project_id)
            if directory.is_dir() and not any(directory.iterdir()):
                await anyio.Path(directory).rmdir()
        except InfrastructureException:
            raise
        except OSError as exc:
            self._raise_storage_error("Không thể dọn thư mục dự án.", exc)

    @override
    async def delete_project_directory(self, project_id: EntityID) -> None:
        """Xóa toàn bộ artifact thuộc dự án mà không block event loop."""
        try:
            directory = self._resolve(str(project_id))
            if directory.is_dir():
                await anyio.to_thread.run_sync(shutil.rmtree, directory)
        except InfrastructureException:
            raise
        except OSError as exc:
            self._raise_storage_error("Không thể xóa artifact dự án.", exc)

    def _resolve(self, value: str | Path) -> Path:
        raw_path = Path(value)
        candidate = raw_path.resolve() if raw_path.is_absolute() else (self._base_dir / raw_path).resolve()
        if not candidate.is_relative_to(self._base_dir):
            raise InfrastructureException(
                code=ErrorCode.STORAGE_ERROR,
                message="Đường dẫn lưu trữ nằm ngoài thư mục được phép.",
            )
        return candidate

    @staticmethod
    def _safe_filename(filename: str) -> str:
        if "/" in filename or "\\" in filename or filename in {".", ".."}:
            raise InfrastructureException(
                code=ErrorCode.STORAGE_ERROR,
                message="Tên file nguồn không hợp lệ.",
            )
        return re.sub(r"[^\w.-]", "_", filename) or "unnamed_file"

    @staticmethod
    def _raise_storage_error(message: str, exc: OSError) -> NoReturn:
        raise InfrastructureException(code=ErrorCode.STORAGE_ERROR, message=message) from exc
