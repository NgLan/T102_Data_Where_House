"""Validation và mapping helpers cho Data Source application service."""

from pathlib import Path

from src.application.data_sources.input import UploadDataSourcesInput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode

MAX_ALLOWED_FILES = 20
MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv", ".docx"}
ALLOWED_COLUMN_TYPES = {"TEXT", "NUMBER", "DATETIME", "BOOLEAN", "OPTION"}


def validate_upload(data: UploadDataSourcesInput) -> None:
    """Kiểm tra batch, extension và kích thước trước khi ghi storage."""
    if not data.files:
        _raise(ErrorCode.FILE_EMPTY, "Danh sách file không được để trống.")
    if len(data.files) > MAX_ALLOWED_FILES:
        _raise(ErrorCode.MAX_FILES_EXCEEDED, f"Chỉ được upload tối đa {MAX_ALLOWED_FILES} file mỗi lần.")
    for item in data.files:
        if extension_of(item.filename) not in ALLOWED_EXTENSIONS:
            _raise(ErrorCode.INVALID_FILE_FORMAT, "Chỉ hỗ trợ file CSV và DOCX.")
        if len(item.content) > MAX_FILE_SIZE:
            _raise(ErrorCode.FILE_TOO_LARGE, f"Mỗi file không được vượt quá {MAX_FILE_SIZE // (1024 * 1024)} MB.")


def validate_column(data_type: str, options: tuple[str, ...]) -> tuple[str, ...]:
    """Chuẩn hóa options và bảo đảm kiểu cột thuộc tập hỗ trợ."""
    if data_type not in ALLOWED_COLUMN_TYPES:
        _raise(ErrorCode.VALIDATION_ERROR, "Kiểu dữ liệu cột không hợp lệ.")
    normalized = tuple(dict.fromkeys(value.strip() for value in options if value.strip()))
    if data_type == "OPTION" and not normalized:
        _raise(ErrorCode.VALIDATION_ERROR, "Cột OPTION phải có ít nhất một lựa chọn.")
    return normalized if data_type == "OPTION" else ()


def extension_of(filename: str) -> str:
    """Lấy extension chữ thường từ tên file."""
    return Path(filename).suffix.lower()


def _raise(code: ErrorCode, message: str) -> None:
    raise BusinessException(code=code, message=message)
