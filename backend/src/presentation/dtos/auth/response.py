"""Response payload an toàn cho Authentication API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.auth.output import CurrentActorOutput


class CurrentActorResponse(BaseModel):
    """Hồ sơ user hiện tại, không chứa credential."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(description="ID actor hiện tại")
    username: str = Field(description="Tên hiển thị của actor")
    email: str = Field(description="Email của actor")
    full_name: str | None = Field(description="Họ tên tùy chọn")
    is_active: bool = Field(description="Tài khoản đang hoạt động")
    created_at: datetime = Field(description="Thời điểm tạo tài khoản")

    @classmethod
    def from_application(cls, output: CurrentActorOutput) -> "CurrentActorResponse":
        """Ánh xạ application output sang HTTP payload."""
        return cls.model_validate(output)
