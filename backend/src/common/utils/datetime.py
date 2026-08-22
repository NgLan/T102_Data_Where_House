"""Utilities xử lý thời gian (datetime.py).

Tuân thủ nguyên tắc:
- Mọi thời gian hệ thống được xử lý theo UTC timezone-aware.
- Không sử dụng datetime.now() naive.
"""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Lấy thời gian hiện tại có timezone UTC.

    Returns:
        Thời gian UTC hiện tại.
    """
    return datetime.now(UTC)


def ensure_utc(dt: datetime) -> datetime:
    """Đảm bảo đối tượng datetime có timezone UTC.

    Args:
        dt: Thời gian cần chuẩn hóa.

    Returns:
        Thời gian có timezone UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def to_isoformat(dt: datetime) -> str:
    """Chuyển thời gian thành chuỗi ISO 8601 UTC.

    Args:
        dt: Thời gian cần chuyển đổi.

    Returns:
        Chuỗi ISO 8601 có timezone UTC.
    """
    utc_dt = ensure_utc(dt)
    return utc_dt.isoformat()


def parse_iso_datetime(value: str) -> datetime:
    """Parse chuỗi ISO 8601 thành đối tượng datetime UTC timezone-aware.

    Args:
        value: Chuỗi ISO 8601 cần phân tích.

    Returns:
        Thời gian có timezone UTC.

    Raises:
        ValueError: Khi chuỗi rỗng hoặc sai định dạng.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Giá trị datetime đầu vào phải là chuỗi không rỗng.")

    try:
        dt = datetime.fromisoformat(value.strip())
        return ensure_utc(dt)
    except ValueError as e:
        raise ValueError(f"Không thể parse ISO datetime từ chuỗi '{value}': {e}") from e
