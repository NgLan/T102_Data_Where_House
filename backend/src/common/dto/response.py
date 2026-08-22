"""DTO envelope cho phản hồi API thành công."""

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Khung phản hồi thành công chuẩn cho toàn bộ hệ thống API.

    {
        "status": "success",
        "code": 200,
        "message": "Xử lý thành công",
        "data": ...,
    }
    """

    model_config = ConfigDict(extra="forbid")

    status: Literal["success"] = Field(
        default="success",
        description="Trạng thái phản hồi (luôn là 'success' đối với 2xx)",
    )
    code: int = Field(
        default=200,
        ge=200,
        le=299,
        description="HTTP Status Code (mặc định 200)",
    )
    message: str = Field(
        default="Xử lý thành công",
        description="Thông điệp phản hồi cho người dùng",
    )
    data: T | None = Field(
        default=None,
        description="Dữ liệu payload chính trả về",
    )
