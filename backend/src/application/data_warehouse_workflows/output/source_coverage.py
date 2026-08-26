"""Application outputs for persisted Source Coverage batches."""

from dataclasses import dataclass

from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import (
    SourceCandidateKind,
    SourceConfirmationStatus,
    SourceCoverageStatus,
)
from src.domain.analytical_requirement.source_coverage import SourceCoverageAssessment
from src.domain.data_source.entities import DataSource
from src.domain.project.entities import Project
from src.domain.requirement.entities import Requirement
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class SourceCoverageCandidateOutput:
    id: EntityID
    kind: SourceCandidateKind
    source_id: EntityID
    source_name: str
    table_name: str | None
    column_name: str | None
    from_column: str | None
    to_column: str | None


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
class _OutputContext:
    requirement_titles: dict[EntityID, str]
    source_names: dict[EntityID, str]


def source_coverage_batch_output(
    project: Project,
    requirements: tuple[Requirement, ...],
    analytical: tuple[AnalyticalRequirement, ...],
    sources: tuple[DataSource, ...],
) -> SourceCoverageBatchOutput | None:
    """Build one typed batch with canonical Requirement and source labels."""
    assessments = _assessment_outputs(requirements, analytical, sources)
    if not assessments:
        return None
    domain = tuple(item for value in analytical for item in value.source_coverage)
    confirmations = tuple(
        item for item in domain
        if item.status is SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION
    )
    resolved = sum(
        item.confirmation_status is not SourceConfirmationStatus.PENDING
        for item in confirmations
    )
    return SourceCoverageBatchOutput(
        domain[0].batch_id,
        domain[0].evaluated_source_revision,
        len(confirmations),
        resolved,
        _can_recheck(project, confirmations),
        assessments,
    )


def _assessment_outputs(
    requirements: tuple[Requirement, ...],
    analytical: tuple[AnalyticalRequirement, ...],
    sources: tuple[DataSource, ...],
) -> tuple[SourceCoverageAssessmentOutput, ...]:
    context = _OutputContext(
        {item.id: item.title for item in requirements},
        {item.id: item.name for item in sources},
    )
    return tuple(
        _assessment_output(item, assessment, context)
        for item in analytical for assessment in item.source_coverage
    )


def _assessment_output(
    analytical: AnalyticalRequirement,
    assessment: SourceCoverageAssessment,
    context: _OutputContext,
) -> SourceCoverageAssessmentOutput:
    candidates = tuple(SourceCoverageCandidateOutput(
        item.id, item.kind, item.source_id, context.source_names.get(item.source_id, ""),
        item.table_name, item.column_name, item.from_column, item.to_column,
    ) for item in assessment.candidates)
    return SourceCoverageAssessmentOutput(
        assessment.id, analytical.id, analytical.requirement_id,
        context.requirement_titles.get(analytical.requirement_id, ""), assessment.status,
        assessment.required_concept_key, assessment.title, assessment.explanation,
        assessment.question, assessment.confirmation_status,
        assessment.selected_candidate_id, assessment.resolution_revision, candidates,
    )


def _can_recheck(
    project: Project, confirmations: tuple[SourceCoverageAssessment, ...]
) -> bool:
    if not confirmations:
        return False
    if any(item.confirmation_status is SourceConfirmationStatus.PENDING for item in confirmations):
        return False
    applied = all(item.applied_source_revision == project.source_revision for item in confirmations)
    current = all(item.evaluated_source_revision == project.source_revision for item in confirmations)
    return applied or (current and not project.is_source_coverage_outdated())
