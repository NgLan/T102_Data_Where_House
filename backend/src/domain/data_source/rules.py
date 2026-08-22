"""Quy tắc nghiệp vụ cho miền Nguồn dữ liệu (Data Source)."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_source.enums import ColumnDataType

MAX_DATA_SOURCE_NAME_LENGTH = 255
ALLOWED_COLUMN_UPDATE_TYPES = frozenset(item.value for item in ColumnDataType)


def normalize_data_source_fields(name: str, location: str) -> tuple[str, str]:
    """Kiểm tra và chuẩn hóa tên, vị trí nguồn dữ liệu.

    Args:
        name: Tên nguồn dữ liệu.
        location: Đường dẫn hoặc địa điểm lưu trữ dữ liệu.
    Returns:
        Cặp tên và vị trí đã loại bỏ khoảng trắng hai đầu.

    Raises:
        BusinessException: Khi tên hoặc vị trí không hợp lệ.
    """
    if not name or not name.strip():
        raise BusinessException(
            code=ErrorCode.INVALID_DATA_SOURCE_NAME,
            message="Tên nguồn dữ liệu không được để trống.",
        )
    if len(name.strip()) > MAX_DATA_SOURCE_NAME_LENGTH:
        raise BusinessException(
            code=ErrorCode.DATA_SOURCE_NAME_TOO_LONG,
            message=f"Tên nguồn dữ liệu vượt quá độ dài tối đa ({MAX_DATA_SOURCE_NAME_LENGTH} ký tự).",
        )
    if not location or not location.strip():
        raise BusinessException(
            code=ErrorCode.INVALID_DATA_SOURCE_LOCATION,
            message="Đường dẫn lưu trữ nguồn dữ liệu (location) không được để trống.",
        )
    return name.strip(), location.strip()


def normalize_column_update(
    table_name: str,
    column_name: str,
    data_type: ColumnDataType | str | None,
) -> tuple[str, str, ColumnDataType | None]:
    """Chuẩn hóa định danh cột và loại dữ liệu cần cập nhật.

    Args:
        table_name: Tên bảng chứa cột.
        column_name: Tên cột cần cập nhật.
        data_type: Loại dữ liệu do client gửi.

    Returns:
        Tên bảng, tên cột đã trim và loại dữ liệu viết hoa.

    Raises:
        BusinessException: Khi định danh rỗng hoặc loại dữ liệu không được hỗ trợ.
    """
    normalized_table = table_name.strip()
    normalized_column = column_name.strip()
    normalized_type = None if data_type is None else str(data_type).strip().upper()
    if not normalized_table or not normalized_column:
        _raise_validation("Tên bảng và tên cột không được để trống.")
    if normalized_type is not None and normalized_type not in ALLOWED_COLUMN_UPDATE_TYPES:
        _raise_validation(f"Loại dữ liệu '{data_type}' không được hỗ trợ.")
    return (
        normalized_table,
        normalized_column,
        ColumnDataType(normalized_type) if normalized_type else None,
    )


def _raise_validation(message: str) -> None:
    """Ném lỗi validation nghiệp vụ thống nhất cho metadata cột."""
    raise BusinessException(code=ErrorCode.VALIDATION_ERROR, message=message)
