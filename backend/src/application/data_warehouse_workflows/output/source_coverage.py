"""Builder cho persisted Source Coverage batches."""

from dataclasses import dataclass

from src.application.data_warehouse_workflows.output.source_coverage_models import (
    SourceCoverageAssessmentOutput,
    SourceCoverageBatchOutput,
    SourceCoverageCandidateOutput,
    SourceCoverageOutputContext,
    SourceCoverageReferenceOutput,
)
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import (
    SourceConfirmationStatus,
    SourceCoverageStatus,
)
from src.domain.analytical_requirement.source_coverage import SourceCoverageAssessment
from src.domain.analytical_requirement.source_coverage_candidate import (
    SourceCoverageCandidate,
)
from src.domain.data_source.entities import DataSource
from src.domain.project.entities import Project
from src.domain.requirement.entities import Requirement
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class _OutputContext:
    requirement_titles: dict[EntityID, str]
    source_names: dict[EntityID, str]


def source_coverage_batch_output(
    project: Project,
    data: SourceCoverageOutputContext,
) -> SourceCoverageBatchOutput | None:
    """Build one typed batch with canonical Requirement and source labels."""
    assessments = _assessment_outputs(data.requirements, data.analytical, data.sources)
    if not assessments:
        return None
    domain = tuple(item for value in data.analytical for item in value.source_coverage)
    confirmations = tuple(item for item in domain if item.status is SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION)
    resolved = sum(item.confirmation_status is not SourceConfirmationStatus.PENDING for item in confirmations)
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
        _assessment_output(item, assessment, context) for item in analytical for assessment in item.source_coverage
    )


def _assessment_output(
    analytical: AnalyticalRequirement,
    assessment: SourceCoverageAssessment,
    context: _OutputContext,
) -> SourceCoverageAssessmentOutput:
    candidates = tuple(_candidate_output(item, context) for item in assessment.candidates)
    return SourceCoverageAssessmentOutput(
        assessment.id,
        analytical.id,
        analytical.requirement_id,
        context.requirement_titles.get(analytical.requirement_id, ""),
        assessment.status,
        assessment.required_concept_key,
        assessment.title,
        assessment.explanation,
        assessment.question,
        assessment.question_type,
        assessment.confirmation_status,
        assessment.selected_candidate_id,
        assessment.resolution_revision,
        candidates,
    )


def _candidate_output(candidate: SourceCoverageCandidate, context: _OutputContext) -> SourceCoverageCandidateOutput:
    references = tuple(
        SourceCoverageReferenceOutput(
            item.kind,
            item.source_id,
            context.source_names.get(item.source_id, ""),
            item.role_key,
            item.role_label,
            item.table_name,
            item.column_name,
            item.from_column,
            item.to_column,
        )
        for item in candidate.references
    )
    return SourceCoverageCandidateOutput(candidate.id, candidate.label, references)


def _can_recheck(project: Project, confirmations: tuple[SourceCoverageAssessment, ...]) -> bool:
    if not confirmations:
        return False
    if any(item.confirmation_status is SourceConfirmationStatus.PENDING for item in confirmations):
        return False
    applied = all(item.applied_source_revision == project.source_revision for item in confirmations)
    current = all(item.evaluated_source_revision == project.source_revision for item in confirmations)
    return applied or (current and not project.is_source_coverage_outdated())


__all__ = [
    "SourceCoverageAssessmentOutput",
    "SourceCoverageBatchOutput",
    "SourceCoverageCandidateOutput",
    "SourceCoverageReferenceOutput",
    "SourceCoverageOutputContext",
    "source_coverage_batch_output",
]
