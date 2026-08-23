"""Typed response payloads của health endpoints."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from src.application.health.models import HealthOutput


class DatabaseHealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    latency_ms: float = Field(ge=0)


class LlmHealthResponse(BaseModel):
    status: Literal["configured", "unconfigured"]
    provider: str
    model: str


class HealthComponentsResponse(BaseModel):
    database: DatabaseHealthResponse
    llm: LlmHealthResponse


class HealthResponse(BaseModel):
    """Trạng thái hoạt động và môi trường hiện tại của Backend."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok", "degraded"] = Field(description="Trạng thái hoạt động")
    env: str = Field(description="Môi trường chạy hiện tại")
    version: str
    timestamp: datetime
    components: HealthComponentsResponse

    @classmethod
    def from_application(cls, output: HealthOutput, timestamp: datetime) -> "HealthResponse":
        return cls(
            status=output.status,
            env=output.env,
            version=output.version,
            timestamp=timestamp,
            components=HealthComponentsResponse(
                database=DatabaseHealthResponse.model_validate(
                    output.database, from_attributes=True
                ),
                llm=LlmHealthResponse.model_validate(output.llm, from_attributes=True),
            ),
        )


class LivenessResponse(BaseModel):
    status: Literal["ok"] = "ok"
    timestamp: datetime


class ReadinessResponse(BaseModel):
    status: Literal["ready"] = "ready"
    timestamp: datetime
    database: DatabaseHealthResponse
