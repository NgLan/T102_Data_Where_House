"""Response payload của health endpoint."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Trạng thái hoạt động và môi trường hiện tại của Backend."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"] = Field(description="Trạng thái hoạt động")
    env: str = Field(description="Môi trường chạy hiện tại")
