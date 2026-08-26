"""Workflow entry point duy nhất của Project Init."""

from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataWarehouseWorkflowService,
)
from src.application.data_warehouse_workflows.input import GenerateDataModelInput, ReanalyzeProjectInput
from src.application.data_warehouse_workflows.output import InputReadinessStatus
from src.application.project_initialization.i_project_initialization_service import (
    IProjectInitializationService,
)
from src.application.project_initialization.models import (
    ProjectInitializationInput,
    ProjectInitializationOutput,
    ProjectInitializationStatus,
)
from src.application.requirements.i_requirement_service import IRequirementService
from src.application.requirements.input import (
    AnalyzeRequirementClarificationInput,
    GetRequirementClarificationInput,
)
from src.application.requirements.output import RequirementClarificationStateOutput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project_session.enums import (
    RequirementClarificationStatus,
    RequirementContinuationState,
)
from typing_extensions import override


class ProjectInitializationService(IProjectInitializationService):
    """Điều phối tuần tự và pause khi RequirementAgent cần làm rõ."""

    def __init__(
        self,
        requirements: IRequirementService,
        data_warehouse: IDataWarehouseWorkflowService,
    ) -> None:
        self._requirements = requirements
        self._data_warehouse = data_warehouse

    @override
    async def run(self, data: ProjectInitializationInput) -> ProjectInitializationOutput:
        state = await self._requirements.get_clarification(GetRequirementClarificationInput(data.project_id))
        if state.is_outdated:
            state = await self._requirements.analyze_clarification(
                AnalyzeRequirementClarificationInput(data.project_id, state.requirement_revision)
            )
        paused_statuses = {
            RequirementClarificationStatus.NEEDS_CLARIFICATION,
            RequirementClarificationStatus.PROCESSING,
        }
        if state.status in paused_statuses:
            return _requirement_pause(state)
        if state.continuation_state in {
            RequirementContinuationState.AWAITING_DECISION,
            RequirementContinuationState.CONTINUE_EDITING,
        }:
            return _requirement_pause(state)
        try:
            analysis = await self._data_warehouse.reanalyze(
                ReanalyzeProjectInput(data.project_id)
            )
            if analysis.readiness_status is not InputReadinessStatus.READY_FOR_DESIGN:
                return ProjectInitializationOutput(
                    ProjectInitializationStatus.PAUSED,
                    readiness_status=analysis.readiness_status,
                    source_coverage_batch=analysis.source_coverage_batch,
                )
            model = await self._data_warehouse.synchronize_data_model(
                GenerateDataModelInput(data.project_id)
            )
        except BusinessException as error:
            return await self._route_downstream_gap(data, state, error)
        return ProjectInitializationOutput(
            ProjectInitializationStatus.COMPLETED,
            data_model_id=model.id,
            readiness_status=InputReadinessStatus.READY_FOR_DESIGN,
            source_coverage_batch=analysis.source_coverage_batch,
        )

    async def _route_downstream_gap(
        self,
        data: ProjectInitializationInput,
        state: RequirementClarificationStateOutput,
        error: BusinessException,
    ) -> ProjectInitializationOutput:
        """Đưa semantic gap về RequirementAgent, không trộn với source gap."""
        if error.code is not ErrorCode.REQUIREMENT_SEMANTIC_CLARIFICATION_REQUIRED:
            raise error
        clarified = await self._requirements.analyze_clarification(
            AnalyzeRequirementClarificationInput(data.project_id, state.requirement_revision)
        )
        if clarified.status is not RequirementClarificationStatus.NEEDS_CLARIFICATION:
            raise error
        session_id = clarified.session.id if clarified.session else None
        return ProjectInitializationOutput(ProjectInitializationStatus.PAUSED, session_id=session_id)


def _requirement_pause(
    state: RequirementClarificationStateOutput,
) -> ProjectInitializationOutput:
    session_id = state.session.id if state.session else None
    return ProjectInitializationOutput(
        ProjectInitializationStatus.PAUSED,
        session_id=session_id,
        readiness_status=InputReadinessStatus.REQUIREMENT_CLARIFICATION_REQUIRED,
    )
