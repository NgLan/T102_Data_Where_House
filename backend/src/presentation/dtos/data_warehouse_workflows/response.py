"""Response payload cho trạng thái phân tích Project."""

from pydantic import BaseModel, ConfigDict, Field
from src.application.data_warehouse_workflows.output import (
    AnalysisStatusOutput,
    InputReadinessStatus,
    RecommendedWorkflowAction,
)
from src.presentation.dtos.source_coverage import SourceCoverageBatchResponse


class AnalysisStatusResponse(BaseModel):
    """Trạng thái outdated và action tiếp theo của workflow."""

    model_config = ConfigDict(from_attributes=True)

    requirement_analysis_outdated: bool = Field(
        description="Raw Requirement cần được phân tích lại"
    )
    source_analysis_outdated: bool = Field(
        description="SchemaMetadata cần được dùng phân tích lại"
    )
    data_model_outdated: bool = Field(description="Data Model không khớp analysis revisions")
    data_model_exists: bool = Field(description="Project đã có Data Model đầu tiên")
    source_revision: int = Field(ge=0, description="Revision dùng cho coverage resolution")
    recommended_action: RecommendedWorkflowAction = Field(
        description="Action UI nên hiển thị tiếp theo"
    )
    readiness_status: InputReadinessStatus
    source_coverage_batch: SourceCoverageBatchResponse | None = None

    @classmethod
    def from_application(cls, output: AnalysisStatusOutput) -> "AnalysisStatusResponse":
        """Ánh xạ application output sang HTTP response."""
        return cls.model_validate(output)
