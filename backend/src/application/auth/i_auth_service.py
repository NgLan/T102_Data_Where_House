"""Interface duy nhất của module Authentication."""

from abc import ABC


class IAuthService(ABC):
    """Hợp đồng application cho các use case Authentication.

    Module chưa có use case được hiện thực; method mới phải được thêm tại đây.
    """
