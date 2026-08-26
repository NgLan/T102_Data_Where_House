"""Transactional persistence for one Source Confirmation item."""

from dataclasses import dataclass

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_warehouse_workflows.input import ResolveSourceCoverageInput
from src.application.data_warehouse_workflows.source_coverage_resolution_rules import (
    ensure_current_resolution,
    resolution_value,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.i_analytical_requirement_repository import (
    IAnalyticalRequirementRepository,
)


@dataclass(slots=True)
class SourceCoverageResolver:
    """Persist one item answer without invoking an Agent or changing revisions."""

    analytical: IAnalyticalRequirementRepository
    unit_of_work: IUnitOfWork
    access: ProjectAccessPolicy

    async def resolve(self, data: ResolveSourceCoverageInput) -> None:
        async with self.unit_of_work:
            project = await self.access.require_owner_for_update(data.project_id)
            items = tuple(await self.analytical.list_by_project(data.project_id))
            owner, index = _find_assessment(items, data.assessment_id)
            assessment = owner.source_coverage[index]
            ensure_current_resolution(project, assessment, data)
            status, candidate_id = resolution_value(assessment, data)
            assessments = list(owner.source_coverage)
            assessments[index] = assessment.with_resolution(status, candidate_id)
            owner.replace_source_coverage(tuple(assessments))
            await self.analytical.save(owner)
            await self.unit_of_work.commit()


def _find_assessment(
    items: tuple[AnalyticalRequirement, ...], assessment_id: object
) -> tuple[AnalyticalRequirement, int]:
    for item in items:
        for index, assessment in enumerate(item.source_coverage):
            if assessment.id == assessment_id:
                return item, index
    raise BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "Coverage assessment không tồn tại.")
