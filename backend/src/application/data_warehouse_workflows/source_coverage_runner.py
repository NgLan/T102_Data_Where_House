"""Evaluate và persist Source Coverage độc lập với analytical derivation."""

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_warehouse_workflows.analysis_helpers import (
    ensure_revision,
    to_requirement_context,
)
from src.application.data_warehouse_workflows.source_coverage_mapper import (
    SourceCoveragePersistenceContext,
    apply_source_coverage,
)
from src.application.data_warehouse_workflows.workflow_data_loader import WorkflowDataReader
from src.application.requirements.i_requirement_service import IRequirementAnalysisAgent
from src.application.requirements.input import EvaluateSourceCoverageInput
from src.application.requirements.output import SourceCoverageResult
from src.common.utils.uuid import generate_uuid
from src.domain.analytical_requirement.i_analytical_requirement_repository import (
    IAnalyticalRequirementRepository,
)
from src.domain.project.entities import Project
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.shared.types import EntityID


class WorkflowSourceCoverageRunner:
    """Chạy coverage khi source revision đổi và persist cả blocking state."""

    def __init__(
        self,
        projects: IProjectRepository,
        analytical: IAnalyticalRequirementRepository,
        agent: IRequirementAnalysisAgent,
        unit_of_work: IUnitOfWork,
        access: ProjectAccessPolicy,
        reader: WorkflowDataReader,
    ) -> None:
        self._projects = projects
        self._analytical = analytical
        self._agent = agent
        self._unit_of_work = unit_of_work
        self._access = access
        self._reader = reader

    async def run(self, project_id: EntityID) -> None:
        project = await self._access.require_owner(project_id)
        if not project.is_source_coverage_outdated():
            return
        data = await self._reader.load_design_input(project.id)
        revisions = (project.analyzed_requirement_revision, project.source_revision)
        if not data.analytical_requirements:
            await self._persist_empty(project.id, revisions)
            return
        contexts = tuple(to_requirement_context(item) for item in data.requirements)
        await self._unit_of_work.rollback()
        result = await self._agent.evaluate_source_coverage(
            EvaluateSourceCoverageInput(contexts, data.analytical_requirements, data.data_sources)
        )
        await self._persist(project.id, revisions, result)

    async def _persist(
        self,
        project_id: EntityID,
        revisions: tuple[int, int],
        result: SourceCoverageResult,
    ) -> None:
        async with self._unit_of_work:
            project = await self._access.require_owner_for_update(project_id)
            _ensure_revisions(project, revisions)
            current = tuple(await self._analytical.list_by_project(project.id))
            updated = apply_source_coverage(
                result,
                current,
                SourceCoveragePersistenceContext(generate_uuid(), revisions[1]),
            )
            await self._analytical.replace_by_project(project.id, updated)
            project.mark_source_analysis_completed()
            await self._projects.save(project)
            await self._unit_of_work.commit()

    async def _persist_empty(self, project_id: EntityID, revisions: tuple[int, int]) -> None:
        async with self._unit_of_work:
            project = await self._access.require_owner_for_update(project_id)
            _ensure_revisions(project, revisions)
            project.mark_source_analysis_completed()
            await self._projects.save(project)
            await self._unit_of_work.commit()


def _ensure_revisions(project: Project, revisions: tuple[int, int]) -> None:
    ensure_revision(project.analyzed_requirement_revision, revisions[0])
    ensure_revision(project.source_revision, revisions[1])
