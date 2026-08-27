"""Structured output của Source Coverage operation."""

from uuid import UUID

from pydantic import Field, model_validator
from src.common.exceptions.business import BusinessException
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationQuestionType,
    SourceCoverageStatus,
)
from src.domain.analytical_requirement.source_confirmation_rules import (
    validate_question_candidates,
)
from src.domain.analytical_requirement.source_coverage_candidate import (
    SourceCoverageCandidate,
    SourceCoverageReference,
)
from src.infrastructure.llm.structured_output_base import AgentOutputBase, GroundedText


class SourceCoverageReferenceItem(AgentOutputBase):
    """Exact source reference được kiểm tra lại bằng code."""

    kind: SourceCandidateKind
    source_ref: str
    role_key: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9_]*$")
    role_label: GroundedText | None = None
    table_name: GroundedText | None = None
    column_name: GroundedText | None = None
    from_column: GroundedText | None = None
    to_column: GroundedText | None = None

    @model_validator(mode="after")
    def validate_shape(self) -> "SourceCoverageReferenceItem":
        try:
            _to_domain_reference(self)
        except BusinessException as exc:
            raise ValueError("Reference fields must match kind and role.") from exc
        return self


class SourceCoverageCandidateItem(AgentOutputBase):
    """Một business answer cùng toàn bộ source evidence cần thiết."""

    label: GroundedText
    references: list[SourceCoverageReferenceItem] = Field(min_length=1)


class SourceCoverageAssessmentItem(AgentOutputBase):
    """Coverage của một required concept với typed answer invariant."""

    status: SourceCoverageStatus
    required_concept_key: GroundedText
    title: GroundedText
    explanation: GroundedText
    question: GroundedText | None = None
    question_type: SourceConfirmationQuestionType | None = None
    candidates: list[SourceCoverageCandidateItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_candidates(self) -> "SourceCoverageAssessmentItem":
        needs_confirmation = self.status is SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION
        has_confirmation = bool(self.question and self.question_type and self.candidates)
        if needs_confirmation != has_confirmation:
            raise ValueError("Confirmation fields must match coverage status.")
        if not needs_confirmation and (self.question or self.question_type or self.candidates):
            raise ValueError("Only source confirmation can contain question fields.")
        if self.question_type is not None:
            _validate_candidate_contract(self.question_type, self.candidates)
        return self


class SourceCoverageOutcomeItem(AgentOutputBase):
    """Coverage của đúng một Analytical Requirement."""

    analytical_requirement_ref: str
    assessments: list[SourceCoverageAssessmentItem] = Field(min_length=1)


class SourceCoverageLlmResult(AgentOutputBase):
    """Tập outcome đầy đủ cho Source Coverage invocation."""

    outcomes: list[SourceCoverageOutcomeItem] = Field(min_length=1)


def _validate_candidate_contract(
    question_type: SourceConfirmationQuestionType,
    candidates: list[SourceCoverageCandidateItem],
) -> None:
    domain_candidates = tuple(
        SourceCoverageCandidate(
            UUID(int=index + 1),
            item.label,
            tuple(_to_domain_reference(reference) for reference in item.references),
        )
        for index, item in enumerate(candidates)
    )
    try:
        validate_question_candidates(question_type, domain_candidates)
    except BusinessException as exc:
        raise ValueError("Candidates do not match question type.") from exc


def _to_domain_reference(item: SourceCoverageReferenceItem) -> SourceCoverageReference:
    return SourceCoverageReference(
        item.kind,
        UUID(int=1),
        item.role_key,
        item.role_label,
        item.table_name,
        item.column_name,
        item.from_column,
        item.to_column,
    )
