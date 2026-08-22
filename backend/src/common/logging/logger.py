"""API lấy logger chuẩn hóa cho các tầng Clean Architecture (logger.py)."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Trả về một Logger instance chuẩn hóa dựa trên name (thường truyền __name__).

    Args:
        name: Tên module, thông thường luôn là ``__name__``.

    Returns:
        Logger chuẩn của Python cho module.
    """
    return logging.getLogger(name)
