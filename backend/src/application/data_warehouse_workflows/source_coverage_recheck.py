"""Materialize one completed confirmation batch before coverage re-evaluation."""

from dataclasses import dataclass

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_warehouse_workflows.input import RecheckSourceCoverageInput
from src.application.data_warehouse_workflows.source_coverage_recheck_rules import (
    apply_candidate,
    ensure_recheckable,
    resolution_candidates,
)
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import SourceConfirmationStatus
from src.domain.analytical_requirement.i_analytical_requirement_repository import (
    IAnalyticalRequirementRepository,
)
from src.domain.analytical_requirement.source_coverage import SourceCoverageAssessment
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import SourceSemanticDecision, SourceSemanticProvenance
from src.domain.data_source.i_data_source_repository import IDataSourceRepository
from src.domain.data_source.semantic_metadata import SourceSemanticAnnotation
from src.domain.project.i_project_repository import IProjectRepository


@dataclass(slots=True)
class SourceCoverageRechecker:
    """Apply USER decisions once; retries only invoke coverage again."""

    projects: IProjectRepository
    analytical: IAnalyticalRequirementRepository
    sources: IDataSourceRepository
    unit_of_work: IUnitOfWork
    access: ProjectAccessPolicy

    async def prepare(self, data: RecheckSourceCoverageInput) -> None:
        async with self.unit_of_work:
            project = await self.access.require_owner_for_update(data.project_id)
            analytical = tuple(await self.analytical.list_by_project(data.project_id))
            batch = _batch_assessments(analytical, data.batch_id)
            if not ensure_recheckable(project, batch, data):
                return
            sources = {
                item.id: item for item in await self.sources.list_by_project(data.project_id)
            }
            _materialize(
                _Materialization(analytical, batch, sources, project.source_revision + 1)
            )
            for source in sources.values():
                await self.sources.save(source)
            for item in analytical:
                await self.analytical.save(item)
            project.increment_source_revision()
            await self.projects.save(project)
            await self.unit_of_work.commit()


def _batch_assessments(
    analytical: tuple[AnalyticalRequirement, ...], batch_id: object
) -> tuple[SourceCoverageAssessment, ...]:
    return tuple(
        assessment for item in analytical for assessment in item.source_coverage
        if assessment.batch_id == batch_id
    )


@dataclass(frozen=True, slots=True)
class _Materialization:
    analytical: tuple[AnalyticalRequirement, ...]
    batch: tuple[SourceCoverageAssessment, ...]
    sources: dict[object, DataSource]
    next_revision: int


def _materialize(data: _Materialization) -> None:
    owners = {
        assessment.id: item
        for item in data.analytical for assessment in item.source_coverage
    }
    for assessment in data.batch:
        if assessment.confirmation_status is None:
            continue
        owner = owners[assessment.id]
        _apply_resolution(owner, assessment, data.sources)
        _mark_applied(owner, assessment.id, data.next_revision)


def _apply_resolution(
    owner: AnalyticalRequirement,
    assessment: SourceCoverageAssessment,
    sources: dict[object, DataSource],
) -> None:
    for source in sources.values():
        source.remove_user_annotation(owner.requirement_id, assessment.required_concept_key)
    decision = (
        SourceSemanticDecision.CONFIRMED
        if assessment.confirmation_status is SourceConfirmationStatus.CONFIRMED
        else SourceSemanticDecision.REJECTED
    )
    annotation = SourceSemanticAnnotation(
        owner.requirement_id,
        assessment.required_concept_key,
        decision,
        SourceSemanticProvenance.USER,
    )
    for candidate in resolution_candidates(assessment):
        apply_candidate(sources, candidate, annotation)


def _mark_applied(
    owner: AnalyticalRequirement, assessment_id: object, source_revision: int
) -> None:
    owner.replace_source_coverage(tuple(
        item.with_applied_source_revision(source_revision)
        if item.id == assessment_id else item
        for item in owner.source_coverage
    ))
