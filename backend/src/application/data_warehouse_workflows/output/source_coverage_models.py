"""Application output models của Source Coverage batch."""

from dataclasses import dataclass

from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationQuestionType,
    SourceConfirmationStatus,
    SourceCoverageStatus,
)
from src.domain.data_source.entities import DataSource
from src.domain.requirement.entities import Requirement
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class SourceCoverageReferenceOutput:
    kind: SourceCandidateKind
    source_id: EntityID
    source_name: str
    role_key: str | None
    role_label: str | None
    table_name: str | None
    column_name: str | None
    from_column: str | None
    to_column: str | None


@dataclass(frozen=True, slots=True)
class SourceCoverageCandidateOutput:
    id: EntityID
    label: str
    references: tuple[SourceCoverageReferenceOutput, ...]


@dataclass(frozen=True, slots=True)
class SourceCoverageAssessmentOutput:
    id: EntityID
    analytical_requirement_id: EntityID
    requirement_id: EntityID
    requirement_title: str
    coverage_status: SourceCoverageStatus
    required_concept_key: str
    title: str
    explanation: str
    question: str | None
    question_type: SourceConfirmationQuestionType | None
    confirmation_status: SourceConfirmationStatus | None
    selected_candidate_id: EntityID | None
    resolution_revision: int
    candidates: tuple[SourceCoverageCandidateOutput, ...]


@dataclass(frozen=True, slots=True)
class SourceCoverageBatchOutput:
    id: EntityID
    evaluated_source_revision: int
    confirmation_total: int
    confirmation_resolved: int
    can_recheck: bool
    assessments: tuple[SourceCoverageAssessmentOutput, ...]


@dataclass(frozen=True, slots=True)
class SourceCoverageOutputContext:
    requirements: tuple[Requirement, ...]
    analytical: tuple[AnalyticalRequirement, ...]
    sources: tuple[DataSource, ...]
