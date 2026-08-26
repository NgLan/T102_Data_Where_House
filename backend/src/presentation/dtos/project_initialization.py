"""Response payload cho workflow Project Init."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.data_warehouse_workflows.output import InputReadinessStatus
from src.application.project_initialization import (
    ProjectInitializationOutput,
    ProjectInitializationStatus,
)
from src.presentation.dtos.source_coverage import SourceCoverageBatchResponse


class ProjectInitializationResponse(BaseModel):
    """Trạng thái workflow cùng resource vừa sẵn sàng."""

    model_config = ConfigDict(from_attributes=True)
    status: ProjectInitializationStatus = Field(description="PAUSED hoặc COMPLETED")
    session_id: UUID | None = Field(default=None, description="Session đang hỏi làm rõ")
    data_model_id: UUID | None = Field(default=None, description="Data Model đã sẵn sàng")
    readiness_status: InputReadinessStatus
    source_coverage_batch: SourceCoverageBatchResponse | None = None

    @classmethod
    def from_application(
        cls, output: ProjectInitializationOutput
    ) -> "ProjectInitializationResponse":
        """Ánh xạ application output sang public payload."""
        return cls.model_validate(output)
