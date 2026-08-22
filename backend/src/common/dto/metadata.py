"""DTO metadata để các payload cụ thể tái sử dụng khi cần."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResponseMeta(BaseModel):
    """Metadata tùy chọn nằm bên trong payload phản hồi."""

    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(
        description="Mã định danh request phục vụ truy vết (X-Request-ID)",
    )
    timestamp: datetime = Field(
        description="Thời gian tạo phản hồi theo ISO 8601",
    )
