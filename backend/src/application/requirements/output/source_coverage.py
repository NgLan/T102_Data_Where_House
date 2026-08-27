"""Typed outputs for the RequirementAgent Source Coverage operation."""

from dataclasses import dataclass

from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationQuestionType,
    SourceCoverageStatus,
)
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class GeneratedSourceCoverageReference:
    kind: SourceCandidateKind
    source_id: EntityID
    role_key: str | None = None
    role_label: str | None = None
    table_name: str | None = None
    column_name: str | None = None
    from_column: str | None = None
    to_column: str | None = None


@dataclass(frozen=True, slots=True)
class GeneratedSourceCoverageCandidate:
    label: str
    references: tuple[GeneratedSourceCoverageReference, ...]


@dataclass(frozen=True, slots=True)
class GeneratedSourceCoverageAssessment:
    status: SourceCoverageStatus
    required_concept_key: str
    title: str
    explanation: str
    question: str | None
    question_type: SourceConfirmationQuestionType | None = None
    candidates: tuple[GeneratedSourceCoverageCandidate, ...] = ()


@dataclass(frozen=True, slots=True)
class SourceCoverageOutcome:
    analytical_requirement_id: EntityID
    assessments: tuple[GeneratedSourceCoverageAssessment, ...]


@dataclass(frozen=True, slots=True)
class SourceCoverageResult:
    outcomes: tuple[SourceCoverageOutcome, ...]
