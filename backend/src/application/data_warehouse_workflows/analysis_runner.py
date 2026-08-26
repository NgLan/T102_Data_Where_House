"""Derive analytical requirements sau Requirement confirmation."""

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_warehouse_workflows.analysis_helpers import (
    ensure_revision,
    to_requirement_context,
)
from src.application.data_warehouse_workflows.analytical_derivation_policy import (
    require_ready_derivation,
)
from src.application.data_warehouse_workflows.generated_entity_mapper import (
    map_generated_analytical,
)
from src.application.data_warehouse_workflows.source_analysis_runner import (
    WorkflowSourceAnalysisRunner,
)
from src.application.data_warehouse_workflows.source_coverage_runner import (
    WorkflowSourceCoverageRunner,
)
from src.application.data_warehouse_workflows.workflow_data_loader import WorkflowDataReader
from src.application.requirements.i_requirement_service import IRequirementAnalysisAgent
from src.application.requirements.input import DeriveAnalyticalRequirementsInput
from src.application.requirements.output import GeneratedAnalyticalRequirement
from src.domain.analytical_requirement.i_analytical_requirement_repository import (
    IAnalyticalRequirementRepository,
)
from src.domain.project.entities import Project
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.shared.types import EntityID


class WorkflowAnalysisRunner:
    """Profile source rồi derive analytical output, không structure Raw Requirement."""

    def __init__(
        self,
        projects: IProjectRepository,
        analytical: IAnalyticalRequirementRepository,
        requirement_agent: IRequirementAnalysisAgent,
        unit_of_work: IUnitOfWork,
        access: ProjectAccessPolicy,
        reader: WorkflowDataReader,
        source_analysis: WorkflowSourceAnalysisRunner,
    ) -> None:
        self._projects = projects
        self._analytical = analytical
        self._requirement_agent = requirement_agent
        self._unit_of_work = unit_of_work
        self._access = access
        self._reader = reader
        self._source_analysis = source_analysis
        self._coverage = WorkflowSourceCoverageRunner(
            projects,
            analytical,
            requirement_agent,
            unit_of_work,
            access,
            reader,
        )

    async def run(self, project_id: EntityID) -> Project:
        """Chạy source/analytical analysis khi Structured Requirement sẵn sàng."""
        project = await self._access.require_owner(project_id)
        await self._source_analysis.analyze_pending(project)
        project = await self._access.require_owner(project_id)
        await self._derive_analytical(project)
        await self._coverage.run(project.id)
        return await self._access.require_owner(project_id)

    async def run_source_coverage(self, project_id: EntityID) -> Project:
        """Chỉ rerun Source Coverage sau khi USER semantic fact thay đổi."""
        await self._coverage.run(project_id)
        return await self._access.require_owner(project_id)

    async def _derive_analytical(self, project: Project) -> None:
        if not project.is_analytical_analysis_outdated():
            return
        data = await self._reader.load_design_input(project.id)
        generated: tuple[GeneratedAnalyticalRequirement, ...] = ()
        if data.requirements:
            await self._unit_of_work.rollback()
            contexts = tuple(to_requirement_context(item) for item in data.requirements)
            result = await self._requirement_agent.derive_analytical_requirements(
                DeriveAnalyticalRequirementsInput(contexts)
            )
            generated = require_ready_derivation(result, contexts)
        await self._save_analytical(
            project.id, project.analyzed_requirement_revision, generated
        )

    async def _save_analytical(
        self,
        project_id: EntityID,
        expected_revision: int,
        generated: tuple[GeneratedAnalyticalRequirement, ...],
    ) -> None:
        async with self._unit_of_work:
            project = await self._access.require_owner_for_update(project_id)
            ensure_revision(project.analyzed_requirement_revision, expected_revision)
            data = await self._reader.load_design_input(project.id)
            valid_ids = {item.id for item in data.requirements}
            entities = map_generated_analytical(generated, valid_ids)
            await self._analytical.replace_by_project(project.id, entities)
            project.mark_analytical_requirements_derived()
            await self._projects.save(project)
            await self._unit_of_work.commit()
