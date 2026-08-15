"""Application service duy nhất của module Authentication."""

from src.application.auth.i_auth_service import IAuthService


class AuthService(IAuthService):
    """Điểm hiện thực tập trung cho các use case Authentication."""
