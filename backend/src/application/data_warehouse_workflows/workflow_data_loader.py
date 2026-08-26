"""Đọc đúng dữ liệu cần cho DWDesignAgent và trạng thái analysis."""

from typing import TypeVar

from src.application.data_warehouse_workflows.input import DataWarehouseDesignInput
from src.application.data_warehouse_workflows.output import (
    AnalysisStatusOutput,
    InputReadinessStatus,
    RecommendedWorkflowAction,
    SourceCoverageBatchOutput,
)
from src.application.data_warehouse_workflows.output.source_coverage import source_coverage_batch_output
from src.domain.analytical_requirement.enums import SourceCoverageStatus
from src.domain.analytical_requirement.i_analytical_requirement_repository import (
    IAnalyticalRequirementRepository,
)
from src.domain.data_model.entities import DataModel
from src.domain.data_model.i_data_model_repository import IDataModelRepository
from src.domain.data_source.i_data_source_repository import IDataSourceRepository
from src.domain.project.entities import Project
from src.domain.requirement.i_requirement_repository import IRequirementRepository
from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID

EntityT = TypeVar("EntityT", bound=BaseEntity)


class WorkflowDataReader:
    """Đọc Agent input và tính trạng thái workflow từ repositories."""

    def __init__(
        self, requirements: IRequirementRepository,
        analytical: IAnalyticalRequirementRepository,
        data_sources: IDataSourceRepository, models: IDataModelRepository,
    ) -> None:
        self._requirements = requirements
        self._analytical = analytical
        self._data_sources = data_sources
        self._models = models

    async def load_design_input(self, project_id: EntityID) -> DataWarehouseDesignInput:
        """Đọc ba nhóm dữ liệu mà DWDesignAgent thực sự sử dụng."""
        requirements = _sorted(await self._requirements.list_by_project(project_id))
        analytical = _sorted(await self._analytical.list_by_project(project_id))
        sources = _sorted(await self._data_sources.list_by_project(project_id))
        return DataWarehouseDesignInput(requirements, analytical, sources)

    async def calculate_analysis_status(self, project: Project) -> AnalysisStatusOutput:
        """Tính trạng thái outdated từ revision, không gọi Agent."""
        model = await self._models.get_by_project_id(project.id)
        data = await self.load_design_input(project.id)
        requirement_outdated = project.is_requirement_analysis_outdated()
        source_outdated = project.is_source_coverage_outdated()
        model_outdated = _is_model_outdated(model, project)
        action = _recommended_action(requirement_outdated, source_outdated, model_outdated)
        coverage = source_coverage_batch_output(
            project, data.requirements, data.analytical_requirements, data.data_sources
        )
        readiness = _readiness(project, requirement_outdated, source_outdated, coverage)
        return AnalysisStatusOutput(
            requirement_outdated, source_outdated, model_outdated,
            model is not None, project.source_revision, action, readiness, coverage,
        )


def _is_model_outdated(model: DataModel | None, project: Project) -> bool:
    """Model chưa tồn tại hoặc không khớp analysis revisions hiện tại."""
    return model is None or model.is_outdated(
        project.analyzed_requirement_revision,
        project.analyzed_source_revision,
    )


def _recommended_action(
    requirement_outdated: bool, source_outdated: bool, model_outdated: bool
) -> RecommendedWorkflowAction:
    """Chọn action tiếp theo theo thứ tự của data flow."""
    if requirement_outdated or source_outdated:
        return RecommendedWorkflowAction.ANALYZE_CHANGES
    if model_outdated:
        return RecommendedWorkflowAction.UPDATE_DATA_MODEL
    return RecommendedWorkflowAction.NONE


def _readiness(
    project: Project,
    requirement_outdated: bool,
    source_outdated: bool,
    coverage: SourceCoverageBatchOutput | None,
) -> InputReadinessStatus:
    if requirement_outdated or project.is_analytical_analysis_outdated():
        return InputReadinessStatus.REQUIREMENT_CLARIFICATION_REQUIRED
    if source_outdated:
        return InputReadinessStatus.SOURCE_DATA_REQUIRED
    statuses = {
        item.coverage_status for item in coverage.assessments
    } if coverage else set()
    if SourceCoverageStatus.MISSING_SOURCE in statuses:
        return InputReadinessStatus.SOURCE_DATA_REQUIRED
    if SourceCoverageStatus.NEEDS_SOURCE_CONFIRMATION in statuses:
        return InputReadinessStatus.SOURCE_CONFIRMATION_REQUIRED
    return InputReadinessStatus.READY_FOR_DESIGN


def _sorted(items: list[EntityT]) -> tuple[EntityT, ...]:
    """Giữ thứ tự Agent input ổn định theo entity ID."""
    return tuple(sorted(items, key=lambda item: str(item.id)))
