"""Input/output độc lập HTTP cho workflow Project Init."""

from dataclasses import dataclass
from enum import StrEnum

from src.application.data_warehouse_workflows.output import (
    InputReadinessStatus,
    SourceCoverageBatchOutput,
)
from src.domain.shared.types import EntityID


class ProjectInitializationStatus(StrEnum):
    """Trạng thái dừng có chủ đích của workflow."""

    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


@dataclass(frozen=True, slots=True)
class ProjectInitializationInput:
    """Project cần chạy workflow từ Requirement đến DBML."""

    project_id: EntityID


@dataclass(frozen=True, slots=True)
class ProjectInitializationOutput:
    """Kết quả workflow hoặc điểm pause chờ clarification."""

    status: ProjectInitializationStatus
    session_id: EntityID | None = None
    data_model_id: EntityID | None = None
    readiness_status: InputReadinessStatus = (
        InputReadinessStatus.REQUIREMENT_CLARIFICATION_REQUIRED
    )
    source_coverage_batch: SourceCoverageBatchOutput | None = None
