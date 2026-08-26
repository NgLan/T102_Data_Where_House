"""Output model cho các thao tác Requirement."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from src.application.project_sessions.clarification_output import ClarificationQuestionOutput
from src.application.project_sessions.output import ProjectSessionOutput
from src.domain.project_session.enums import (
    RequirementClarificationStatus,
    RequirementContinuationState,
)
from src.domain.requirement.entities import Requirement
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class RequirementOutput:
    """Snapshot Requirement được phép đi qua application boundary."""

    id: EntityID
    project_id: EntityID
    title: str
    description: str
    type: RequirementType
    priority: RequirementPriority
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, requirement: Requirement) -> "RequirementOutput":
        """Ánh xạ domain entity sang application output."""
        return cls(
            id=requirement.id,
            project_id=requirement.project_id,
            title=requirement.title,
            description=requirement.description,
            type=requirement.type,
            priority=requirement.priority,
            created_at=requirement.created_at,
            updated_at=requirement.updated_at,
        )


@dataclass(frozen=True, slots=True)
class GeneratedRequirement:
    """Structured Requirement do Agent sinh, chưa phải Domain entity."""

    title: str
    description: str
    requirement_type: RequirementType
    priority: RequirementPriority
    existing_requirement_id: EntityID | None = None


@dataclass(frozen=True, slots=True)
class GeneratedAnalyticalRequirement:
    """Analytical Requirement do Agent sinh."""

    source_requirement_id: EntityID
    metric: str | None
    dimension: str | None
    time_granularity: str | None
    aggregation_method: str | None
    grain: str | None


class AnalyticalDerivationStatus(StrEnum):
    """Kết luận truy vết cho từng Structured Requirement."""

    READY = "READY"
    NEEDS_REQUIREMENT_CLARIFICATION = "NEEDS_REQUIREMENT_CLARIFICATION"
    NOT_ANALYTICAL = "NOT_ANALYTICAL"


@dataclass(frozen=True, slots=True)
class AnalyticalDerivationOutcome:
    """Kết quả derivation của đúng một Structured Requirement."""

    source_requirement_id: EntityID
    status: AnalyticalDerivationStatus
    analytical_requirements: tuple[GeneratedAnalyticalRequirement, ...] = ()
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class AnalyticalDerivationResult:
    """Tập kết quả đầy đủ, không được âm thầm bỏ Requirement."""

    outcomes: tuple[AnalyticalDerivationOutcome, ...]


@dataclass(frozen=True, slots=True)
class RequirementClarificationResult:
    """Structured kết quả của đúng một clarification turn."""

    requirements: tuple[GeneratedRequirement, ...]
    status: RequirementClarificationStatus
    question: str | None = None
    options: tuple[str, ...] = ()
    allow_custom_answer: bool = False
    reason: str | None = None
    summary: str | None = None


@dataclass(frozen=True, slots=True)
class RequirementClarificationStateOutput:
    """UI state dẫn xuất từ Project revision và session lifecycle."""

    session: ProjectSessionOutput | None
    status: RequirementClarificationStatus
    pending_question: ClarificationQuestionOutput | None
    requirements: tuple[RequirementOutput, ...]
    requirement_revision: int
    analyzed_requirement_revision: int
    is_outdated: bool
    continuation_state: RequirementContinuationState
