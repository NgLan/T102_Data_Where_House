"""Application tests cho deterministic Data Warehouse workflow."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.data_warehouse_workflows.data_warehouse_workflow_service import (
    DataWarehouseWorkflowService,
)
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataModelValidationEngine,
    IDataWarehouseDesignAgent,
    IRequirementAnalysisAgent,
)
from src.application.data_warehouse_workflows.input import (
    AnalyticalAnalysisInput,
    ConversationDesignInput,
    CreateAiEditProposalInput,
    DataWarehouseDesignInput,
    GenerateDataModelInput,
    GetAnalysisStatusInput,
    RawRequirementAnalysisInput,
    ReanalyzeProjectInput,
    RegenerateDataModelInput,
    RevisionDesignInput,
)
from src.application.data_warehouse_workflows.output import (
    AgentTurnKind,
    ConversationDesignResult,
    GeneratedAnalyticalRequirement,
    GeneratedDbml,
    GeneratedRequirement,
    ValidationIssue,
    ValidationIssueCode,
    ValidationSeverity,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_source.entities import DataSource
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata, TableMetadata
from src.domain.project.entities import Project
from typing_extensions import override

from tests.fakes import (
    FakeAnalyticalRequirementRepository,
    FakeDataModelRepository,
    FakeDataSourceRepository,
    FakeProjectMemberRepository,
    FakeProjectRepository,
    FakeRequirementRepository,
    FakeUnitOfWork,
)
from tests.test_application.test_data_model_use_cases import FakeChangeRepository

VALID_DBML = "Table Fact_Rides {\n  ride_key int [pk]\n}"


class RecordingRequirementAgent(IRequirementAnalysisAgent):
    """Fake ghi số lần gọi hai operation."""

    def __init__(self) -> None:
        self.raw_calls = 0
        self.analytical_calls = 0

    @override
    async def structure_raw_requirement(
        self, data: RawRequirementAnalysisInput
    ) -> tuple[GeneratedRequirement, ...]:
        self.raw_calls += 1
        return (GeneratedRequirement("Revenue", data.raw_requirement, "ANALYTICAL", "HIGH"),)

    @override
    async def derive_analytical_requirements(
        self, data: AnalyticalAnalysisInput
    ) -> tuple[GeneratedAnalyticalRequirement, ...]:
        self.analytical_calls += 1
        requirement_id = data.requirements[0].id
        return (
            GeneratedAnalyticalRequirement(
                requirement_id, "revenue", "month", "MONTH", "SUM", "one ride"
            ),
        )


class RecordingDesignAgent(IDataWarehouseDesignAgent):
    """Fake DWDesignAgent trả lần lượt DBML cấu hình sẵn."""

    def __init__(self, results: list[str] | None = None) -> None:
        self.results = results or [VALID_DBML]
        self.calls: list[object] = []

    @override
    async def generate(self, data: DataWarehouseDesignInput) -> GeneratedDbml:
        self.calls.append(data)
        return GeneratedDbml(self.results[min(len(self.calls) - 1, len(self.results) - 1)])

    @override
    async def revise(self, data: RevisionDesignInput) -> GeneratedDbml:
        self.calls.append(data)
        return GeneratedDbml(self.results[min(len(self.calls) - 1, len(self.results) - 1)])

    @override
    async def converse(self, data: ConversationDesignInput) -> ConversationDesignResult:
        self.calls.append(data)
        dbml = self.results[min(len(self.calls) - 1, len(self.results) - 1)]
        return ConversationDesignResult(AgentTurnKind.PROPOSAL, dbml=dbml)


class FailingAnalyticalAgent(RecordingRequirementAgent):
    """Fake mô phỏng operation Analytical Requirement thất bại."""

    @override
    async def derive_analytical_requirements(
        self, data: AnalyticalAnalysisInput
    ) -> tuple[GeneratedAnalyticalRequirement, ...]:
        del data
        raise RuntimeError("provider failed")

class MarkerValidator(IDataModelValidationEngine):
    """Coi chuỗi bắt đầu bằng invalid là validation ERROR."""

    @override
    def validate(self, dbml: str) -> tuple[ValidationIssue, ...]:
        if not dbml.startswith("invalid"):
            return ()
        return (
            ValidationIssue(
                code=ValidationIssueCode.DBML_SYNTAX_INVALID,
                severity=ValidationSeverity.ERROR,
                title="DBML không hợp lệ",
                description="invalid dbml",
            ),
        )


def _build_workflow(
    project: Project,
    requirement_agent: RecordingRequirementAgent,
    design_agent: RecordingDesignAgent,
    sources: list[DataSource] | None = None,
) -> tuple[
    DataWarehouseWorkflowService,
    FakeDataModelRepository,
    FakeChangeRepository,
    FakeUnitOfWork,
]:
    projects = FakeProjectRepository([project])
    models = FakeDataModelRepository([])
    changes = FakeChangeRepository([])
    unit_of_work = FakeUnitOfWork()
    access = ProjectAccessPolicy(
        projects, FakeProjectMemberRepository([]), project.user_id
    )
    source_analysis = MagicMock()
    source_analysis.analyze_pending = AsyncMock()
    service = DataWarehouseWorkflowService(
        projects,
        FakeRequirementRepository([]),
        FakeAnalyticalRequirementRepository([]),
        FakeDataSourceRepository(sources or []),
        models,
        changes,
        requirement_agent,
        source_analysis,
        design_agent,
        MarkerValidator(),
        unit_of_work,
        access,
    )
    return service, models, changes, unit_of_work


@pytest.mark.asyncio
async def test_initial_flow_calls_two_requirement_operations_and_design_once() -> None:
    """Save & Analyze tạo model bằng ba Agent invocations logic."""
    project = Project(name="Demo", requirement="Track revenue", user_id=uuid4())
    requirement_agent = RecordingRequirementAgent()
    design_agent = RecordingDesignAgent()
    workflow, models, _, unit_of_work = _build_workflow(
        project, requirement_agent, design_agent
    )

    output = await workflow.generate_data_model(GenerateDataModelInput(project.id))

    assert output.dbml == VALID_DBML
    assert requirement_agent.raw_calls == 1
    assert requirement_agent.analytical_calls == 1
    assert len(design_agent.calls) == 1
    assert models._items[0].generated_from_requirement_revision == 1
    assert models._items[0].generated_from_source_revision == 0
    assert project.analyzed_requirement_revision == project.requirement_revision
    assert project.analyzed_source_revision == project.source_revision
    assert unit_of_work.rollback_count == 3


@pytest.mark.asyncio
async def test_unchanged_analysis_calls_no_agent() -> None:
    """Analysis revisions bằng nhau ngăn gọi LLM thừa."""
    project = Project(name="Demo", requirement="Track revenue", user_id=uuid4())
    requirement_agent = RecordingRequirementAgent()
    workflow, _, _, _ = _build_workflow(
        project, requirement_agent, RecordingDesignAgent()
    )
    await workflow.reanalyze(ReanalyzeProjectInput(project.id))

    await workflow.reanalyze(ReanalyzeProjectInput(project.id))

    assert requirement_agent.raw_calls == 1
    assert requirement_agent.analytical_calls == 1


@pytest.mark.asyncio
async def test_source_change_only_repeats_analytical_operation() -> None:
    """SchemaMetadata đổi không gọi lại Raw Requirement operation."""
    project = Project(name="Demo", requirement="Track revenue", user_id=uuid4())
    requirement_agent = RecordingRequirementAgent()
    source = DataSource(
        project_id=project.id,
        name="rides",
        location="rides.csv",
        schema_metadata=SchemaMetadata(
            tables=(TableMetadata("rides", (ColumnMetadata("id", "INTEGER"),)),)
        ),
    )
    workflow, _, _, _ = _build_workflow(
        project, requirement_agent, RecordingDesignAgent(), [source]
    )
    await workflow.reanalyze(ReanalyzeProjectInput(project.id))
    source.schema_metadata = SchemaMetadata(
        tables=(TableMetadata("rides", (ColumnMetadata("amount", "DECIMAL"),)),)
    )
    project.increment_source_revision()

    await workflow.reanalyze(ReanalyzeProjectInput(project.id))

    assert requirement_agent.raw_calls == 1
    assert requirement_agent.analytical_calls == 2


@pytest.mark.asyncio
async def test_failed_analysis_does_not_advance_analyzed_revisions() -> None:
    """Agent thất bại giữ nguyên analyzed revisions để lần sau có thể chạy lại."""
    project = Project(name="Demo", requirement="Track revenue", user_id=uuid4())
    workflow, _, _, _ = _build_workflow(
        project, FailingAnalyticalAgent(), RecordingDesignAgent()
    )

    with pytest.raises(RuntimeError, match="provider failed"):
        await workflow.reanalyze(ReanalyzeProjectInput(project.id))

    assert project.analyzed_requirement_revision == 0
    assert project.analyzed_source_revision == 0


@pytest.mark.asyncio
async def test_validation_retry_passes_failed_dbml_and_stops_at_success() -> None:
    """Retry thuộc Application orchestration, không nằm trong Agent."""
    project = Project(name="Demo", requirement="Track revenue", user_id=uuid4())
    design_agent = RecordingDesignAgent(["invalid first", VALID_DBML])
    workflow, _, _, _ = _build_workflow(
        project, RecordingRequirementAgent(), design_agent
    )

    await workflow.generate_data_model(GenerateDataModelInput(project.id))

    assert len(design_agent.calls) == 2
    assert design_agent.calls[1].failed_dbml == "invalid first"
    assert design_agent.calls[1].validation_issues


@pytest.mark.asyncio
async def test_regenerate_overwrites_model_without_creating_proposal() -> None:
    """Update Data Model ghi đè trực tiếp, tăng revision và không tạo proposal."""
    project = Project(name="Demo", requirement="Track revenue", user_id=uuid4())
    regenerated_dbml = "Table Fact_Rides {\n  ride_key int [pk]\n  amount decimal\n}"
    workflow, models, changes, _ = _build_workflow(
        project,
        RecordingRequirementAgent(),
        RecordingDesignAgent([VALID_DBML, regenerated_dbml]),
    )
    initial = await workflow.generate_data_model(GenerateDataModelInput(project.id))

    regenerated = await workflow.regenerate_data_model(RegenerateDataModelInput(project.id))

    assert regenerated.id == initial.id
    assert regenerated.dbml == regenerated_dbml
    assert regenerated.revision == initial.revision + 1
    assert changes.items == []


@pytest.mark.asyncio
async def test_generate_conflicts_when_model_already_exists() -> None:
    """Generate là create-only và không được ghi đè snapshot hiện hành."""
    project = Project(name="Demo", requirement="Track revenue", user_id=uuid4())
    design_agent = RecordingDesignAgent()
    workflow, _, _, _ = _build_workflow(
        project,
        RecordingRequirementAgent(),
        design_agent,
    )
    await workflow.generate_data_model(GenerateDataModelInput(project.id))

    with pytest.raises(BusinessException) as raised:
        await workflow.generate_data_model(GenerateDataModelInput(project.id))

    assert raised.value.code == ErrorCode.DATA_MODEL_ALREADY_EXISTS
    assert len(design_agent.calls) == 1


@pytest.mark.asyncio
async def test_reanalyze_never_mutates_existing_model() -> None:
    """Reanalyze chỉ cập nhật analysis và giữ nguyên snapshot/revision Data Model."""
    project = Project(name="Demo", requirement="Track revenue", user_id=uuid4())
    workflow, models, _, _ = _build_workflow(
        project,
        RecordingRequirementAgent(),
        RecordingDesignAgent(),
    )
    await workflow.generate_data_model(GenerateDataModelInput(project.id))
    original_dbml = models._items[0].dbml
    original_revision = models._items[0].revision
    project.increment_requirement_revision()

    await workflow.reanalyze(ReanalyzeProjectInput(project.id))

    assert models._items[0].dbml == original_dbml
    assert models._items[0].revision == original_revision


@pytest.mark.asyncio
async def test_regenerate_rejects_persistence_revision_race() -> None:
    """Optimistic write thất bại sau LLM phải trả conflict và không commit."""
    project = Project(name="Demo", requirement="Track revenue", user_id=uuid4())
    workflow, models, _, unit_of_work = _build_workflow(
        project,
        RecordingRequirementAgent(),
        RecordingDesignAgent([VALID_DBML, VALID_DBML]),
    )
    await workflow.generate_data_model(GenerateDataModelInput(project.id))

    async def reject_update(entity: object, base_revision: int) -> None:
        del entity, base_revision
        return None

    models.update_if_revision_matches = reject_update  # type: ignore[method-assign]

    with pytest.raises(BusinessException) as raised:
        await workflow.regenerate_data_model(RegenerateDataModelInput(project.id))

    assert raised.value.code == ErrorCode.DATA_MODEL_REVISION_CONFLICT
    assert unit_of_work.commit_count == 3


@pytest.mark.asyncio
async def test_ai_edit_still_creates_proposal_without_overwrite() -> None:
    """AI edit giữ Human Review và base revision hiện hành."""
    project = Project(name="Demo", requirement="Track revenue", user_id=uuid4())
    revised_dbml = "Table Fact_Rides {\n  ride_key int [pk]\n  note varchar\n}"
    workflow, models, changes, _ = _build_workflow(
        project,
        RecordingRequirementAgent(),
        RecordingDesignAgent([VALID_DBML, revised_dbml]),
    )
    initial = await workflow.generate_data_model(GenerateDataModelInput(project.id))

    proposal = await workflow.create_ai_edit_proposal(
        CreateAiEditProposalInput(project.id, "Thêm ghi chú")
    )

    assert models._items[0].dbml == initial.dbml
    assert proposal.summary.base_revision == initial.revision
    assert proposal.proposed_dbml == revised_dbml
    assert len(changes.items) == 1


@pytest.mark.asyncio
async def test_legacy_model_without_generated_revisions_is_outdated() -> None:
    """Model cũ thiếu generated revisions cần Update Data Model."""
    project = Project(name="Demo", requirement="Track revenue", user_id=uuid4())
    workflow, models, _, _ = _build_workflow(
        project, RecordingRequirementAgent(), RecordingDesignAgent()
    )
    await workflow.generate_data_model(GenerateDataModelInput(project.id))
    models._items[0].generated_from_requirement_revision = 0

    status = await workflow.get_analysis_status(GetAnalysisStatusInput(project.id))

    assert status.data_model_exists is True
    assert status.data_model_outdated is True


def test_project_derives_outdated_state_from_revisions() -> None:
    """Project không persist derived outdated flags."""
    project = Project(name="Demo", requirement="Track revenue", user_id=uuid4())

    assert project.is_requirement_analysis_outdated() is True
    assert project.is_source_analysis_outdated() is False

    project.mark_requirement_analysis_completed()
    project.increment_source_revision()

    assert project.is_requirement_analysis_outdated() is False
    assert project.is_source_analysis_outdated() is True
