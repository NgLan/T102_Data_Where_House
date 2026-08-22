"""Utilities xử lý chuỗi văn bản (string.py).

Tuân thủ nguyên tắc:
- Không over-normalize (không tự động lowercase hoặc xóa dấu tiếng Việt/tiếng Nhật trừ khi yêu cầu).
- Pure function, xử lý an toàn với chuỗi rỗng và None.
"""

import re

WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_whitespace(value: str) -> str:
    """Chuẩn hóa các khoảng trắng liên tiếp trong chuỗi.

    Args:
        value: Chuỗi cần chuẩn hóa.

    Returns:
        Chuỗi đã bỏ khoảng trắng thừa.

    Raises:
        TypeError: Khi đầu vào không phải chuỗi.
    """
    if not isinstance(value, str):
        raise TypeError("Giá trị đầu vào phải là chuỗi (str).")
    return WHITESPACE_PATTERN.sub(" ", value.strip())


def is_blank(value: str | None) -> bool:
    """Kiểm tra chuỗi là ``None``, rỗng hoặc chỉ có khoảng trắng.

    Args:
        value: Chuỗi cần kiểm tra.

    Returns:
        ``True`` khi chuỗi không có nội dung.
    """
    if value is None:
        return True
    return len(value.strip()) == 0


def truncate(value: str, max_length: int, suffix: str = "...") -> str:
    """Cắt ngắn chuỗi nếu vượt quá max_length và gắn suffix ở cuối.

    Args:
        value: Chuỗi cần cắt.
        max_length: Độ dài tối đa của kết quả.
        suffix: Hậu tố đánh dấu chuỗi đã bị cắt.

    Returns:
        Chuỗi gốc hoặc chuỗi đã cắt kèm hậu tố.

    Raises:
        TypeError: Khi đầu vào không phải chuỗi.
        ValueError: Khi độ dài tối đa không lớn hơn hậu tố.
    """
    if not isinstance(value, str):
        raise TypeError("Giá trị đầu vào phải là chuỗi (str).")

    if max_length <= len(suffix):
        raise ValueError(f"max_length ({max_length}) phải lớn hơn độ dài suffix ({len(suffix)}).")

    if len(value) <= max_length:
        return value

    return value[: max_length - len(suffix)] + suffix


def safe_strip(value: str | None) -> str | None:
    """Bỏ khoảng trắng đầu cuối và bảo toàn ``None``.

    Args:
        value: Chuỗi cần xử lý hoặc ``None``.

    Returns:
        Chuỗi đã xử lý hoặc ``None``.
    """
    if value is None:
        return None
    return value.strip()
