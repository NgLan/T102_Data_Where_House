"""Structured output của Source Coverage operation."""

from uuid import UUID

from pydantic import Field, model_validator
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceCoverageStatus,
)
from src.infrastructure.llm.structured_output_base import AgentOutputBase, GroundedText


class SourceCoverageCandidateItem(AgentOutputBase):
    """Exact source reference được kiểm tra lại bằng code."""

    kind: SourceCandidateKind
    source_id: UUID
    table_name: GroundedText | None = None
    column_name: GroundedText | None = None
    from_column: GroundedText | None = None
    to_column: GroundedText | None = None

    @model_validator(mode="after")
    def validate_shape(self) -> "SourceCoverageCandidateItem":
        if self.kind is SourceCandidateKind.COLUMN:
            valid = bool(self.table_name and self.column_name)
            valid = valid and self.from_column is None and self.to_column is None
        else:
            valid = bool(self.from_column and self.to_column)
            valid = valid and self.table_name is None and self.column_name is None
        if not valid:
            raise ValueError("Candidate fields must match candidate kind.")
        return self


class SourceCoverageAssessmentItem(AgentOutputBase):
    """Coverage của một required concept với candidate invariant rõ ràng."""

    status: SourceCoverageStatus
    required_concept_key: GroundedText
    title: GroundedText
    explanation: GroundedText
    question: GroundedText | None = None
    candidates: list[SourceCoverageCandidateItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_candidates(self) -> "SourceCoverageAssessmentItem":
        if self.status is SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION:
            if not self.candidates:
                raise ValueError("NEEDS_SOURCE_CONFIRMATION requires candidates.")
            if not self.question:
                raise ValueError("NEEDS_SOURCE_CONFIRMATION requires a question.")
        if self.status is SourceCoverageStatus.MISSING_SOURCE and self.candidates:
            raise ValueError("MISSING_SOURCE cannot contain candidates.")
        if self.status is not SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION:
            self.question = None
        return self


class SourceCoverageOutcomeItem(AgentOutputBase):
    """Coverage của đúng một Analytical Requirement."""

    analytical_requirement_id: UUID
    assessments: list[SourceCoverageAssessmentItem] = Field(min_length=1)


class SourceCoverageLlmResult(AgentOutputBase):
    """Tập outcome đầy đủ cho Source Coverage invocation."""

    outcomes: list[SourceCoverageOutcomeItem] = Field(min_length=1)
