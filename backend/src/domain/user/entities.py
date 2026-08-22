"""Thực thể Người dùng (User Entity)."""

from dataclasses import dataclass

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.shared.entity import BaseEntity
from src.domain.user.value_objects import Email

MAX_USERNAME_LENGTH = 100


@dataclass(eq=False, kw_only=True)
class User(BaseEntity):
    """Thực thể đại diện cho Người dùng (User) trong hệ thống."""

    username: str
    email: Email

    def __post_init__(self) -> None:
        """Thực thi kiểm tra và đảm bảo invariant cho User."""
        super().__post_init__()

        if isinstance(self.email, str):
            self.email = Email(self.email)
        elif not isinstance(self.email, Email):
            raise BusinessException(
                code=ErrorCode.INVALID_EMAIL,
                message="Trường email phải là một đối tượng Email hợp lệ.",
            )

        self._validate_and_normalize_username()

    def _validate_and_normalize_username(self) -> None:
        """Kiểm tra và chuẩn hóa tên người dùng."""
        if not isinstance(self.username, str) or not self.username.strip():
            raise BusinessException(
                code=ErrorCode.INVALID_USERNAME,
                message="Tên người dùng không được để trống.",
            )

        normalized = self.username.strip()
        if len(normalized) > MAX_USERNAME_LENGTH:
            raise BusinessException(
                code=ErrorCode.USERNAME_TOO_LONG,
                message=f"Tên người dùng vượt quá độ dài tối đa ({MAX_USERNAME_LENGTH} ký tự).",
            )

        self.username = normalized

