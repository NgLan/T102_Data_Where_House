"""Utilities xử lý UUID (uuid.py).

Cung cấp các hàm trợ giúp khởi tạo và kiểm tra tính hợp lệ của UUIDv4.
"""

import uuid


def generate_uuid() -> uuid.UUID:
    """Sinh một UUID phiên bản 4 ngẫu nhiên.

    Returns:
        UUID phiên bản 4 mới.
    """
    return uuid.uuid4()


def generate_uuid_str() -> str:
    """Sinh chuỗi UUID phiên bản 4 dạng chuẩn 36 ký tự.

    Returns:
        Chuỗi UUID phiên bản 4 mới.
    """
    return str(uuid.uuid4())


def is_valid_uuid(val: str | uuid.UUID) -> bool:
    """Kiểm tra một giá trị có phải là UUID (v4) hợp lệ hay không.

    Args:
        val: UUID hoặc chuỗi UUID dạng chuẩn cần kiểm tra.

    Returns:
        ``True`` khi giá trị là UUID phiên bản 4 hợp lệ.
    """
    if isinstance(val, uuid.UUID):
        return val.version == 4

    if not isinstance(val, str):
        return False

    try:
        parsed = uuid.UUID(val.strip())
        return parsed.version == 4 and str(parsed) == val.strip().lower()
    except (ValueError, AttributeError):
        return False
