"""Value objects cho miền Người dùng."""

from dataclasses import dataclass

from email_validator import EmailNotValidError, validate_email
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.shared.value_object import BaseValueObject

MAX_EMAIL_LENGTH = 255


@dataclass(frozen=True)
class Email(BaseValueObject):
    """Value Object đại diện cho địa chỉ Email hợp lệ."""

    value: str

    def __post_init__(self) -> None:
        """Kiểm tra và chuẩn hóa địa chỉ email.

        Raises:
            BusinessException: Khi email rỗng, quá dài hoặc sai cú pháp.
        """
        if not isinstance(self.value, str) or not self.value.strip():
            _raise_invalid_email("Địa chỉ email không được để trống.")
        if len(self.value.strip()) > MAX_EMAIL_LENGTH:
            _raise_invalid_email("Địa chỉ email vượt quá độ dài tối đa 255 ký tự.")
        try:
            result = validate_email(self.value.strip(), check_deliverability=False)
        except EmailNotValidError as exc:
            raise BusinessException(
                code=ErrorCode.INVALID_EMAIL,
                message="Địa chỉ email không đúng định dạng.",
            ) from exc
        object.__setattr__(self, "value", result.normalized)


def _raise_invalid_email(message: str) -> None:
    """Ném lỗi nghiệp vụ thống nhất cho email không hợp lệ."""
    raise BusinessException(code=ErrorCode.INVALID_EMAIL, message=message)
