"""Unit tests cho Agent operation không dùng graph hoặc tool loop."""

from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError
from src.application.data_warehouse_workflows.input import (
    ConversationDesignInput,
    DataWarehouseDesignInput,
    RevisionDesignInput,
)
from src.application.project_sessions.conversation_context import (
    ConversationInputKind,
    ConversationMemory,
)
from src.application.requirements.input import (
    ClarifyRequirementsInput,
    DeriveAnalyticalRequirementsInput,
    RequirementContext,
)
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.data_source.entities import DataSource
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata, TableMetadata
from src.domain.requirement.entities import Requirement
from src.infrastructure.agents.data_warehouse_design_agent import DataWarehouseDesignAgent
from src.infrastructure.agents.prompts.dw_conversation import DW_CONVERSATION_SYSTEM_PROMPT
from src.infrastructure.agents.requirement_analysis_agent import RequirementAnalysisAgent
from src.infrastructure.llm.agent_structured_outputs import (
    AnalyticalDerivationOutcome,
    AnalyticalRequirementItem,
    AnalyticalRequirementResult,
    DbmlRevisionResult,
    DwConversationResult,
    GeneratedRequirementItem,
    RequirementClarificationResult,
)
from src.infrastructure.security.pii_guard import PiiGuard

DBML = "Table Fact_Rides {\n  ride_key int [pk]\n}"


def _conversation_input(revision: RevisionDesignInput) -> ConversationDesignInput:
    memory = ConversationMemory(
        None,
        (),
        revision.instruction or "",
        ConversationInputKind.USER_MESSAGE,
    )
    return ConversationDesignInput(revision, memory)


def test_conversation_schema_requires_branch_payload_keys() -> None:
    """JSON Schema gửi cho LLM phải bắt buộc cả question và dbml."""
    required = set(DwConversationResult.model_json_schema()["required"])

    assert {
        "kind",
        "question",
        "options",
        "allow_custom_answer",
        "reason",
        "dbml",
        "summary",
    } <= required


def test_conversation_proposal_accepts_complete_dbml() -> None:
    """Proposal hợp lệ mang nguyên tài liệu DBML và không cần câu hỏi."""
    result = DwConversationResult(
        kind="proposal",
        question=None,
        options=[],
        allow_custom_answer=False,
        reason=None,
        dbml=DBML,
        summary="Đã cập nhật mô hình.",
    )

    assert result.dbml == DBML


def test_clarification_has_grounded_options_and_custom_answer() -> None:
    result = DwConversationResult(
        kind="clarification",
        question="Bạn muốn phân tích doanh thu theo mức thời gian nào?",
        options=["Theo ngày", "Theo tháng", "Theo quý"],
        allow_custom_answer=True,
        reason="Time granularity chưa được xác định.",
        dbml=None,
        summary="Cần làm rõ time granularity.",
    )

    assert len(result.options) == 3
    assert result.allow_custom_answer is True


def test_clarification_rejects_more_than_four_options() -> None:
    with pytest.raises(ValidationError):
        DwConversationResult(
            kind="clarification",
            question="Chọn grain?",
            options=["A", "B", "C", "D", "E"],
            allow_custom_answer=True,
            reason=None,
            dbml=None,
            summary="Cần làm rõ grain.",
        )


def test_prompt_asks_only_for_material_design_ambiguity() -> None:
    prompt = DW_CONVERSATION_SYSTEM_PROMPT.casefold()

    assert "grain" in prompt
    assert "multiple reasonable interpretations" in prompt
    assert "do not ask about minor uncertainty" in prompt


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("instruction", "question", "options"),
    [
        (
            "Theo dõi doanh thu nhưng chưa xác định grain",
            "Bạn muốn grain của Fact_Revenue là gì?",
            ["Một giao dịch", "Một dòng sản phẩm"],
        ),
        (
            "Doanh thu có thể là gross hoặc net",
            "Bạn muốn dùng định nghĩa doanh thu nào?",
            ["Gross revenue", "Net revenue"],
        ),
    ],
)
async def test_material_ambiguity_maps_to_one_question(
    instruction: str,
    question: str,
    options: list[str],
) -> None:
    model = _model()
    model.results[DwConversationResult] = DwConversationResult(
        kind="clarification",
        question=question,
        options=options,
        allow_custom_answer=True,
        reason="Quyết định ảnh hưởng thiết kế Fact.",
        dbml=None,
        summary="Cần một thông tin làm rõ.",
    )
    agent = DataWarehouseDesignAgent(model, PiiGuard(enabled=False))

    result = await agent.converse(_conversation_input(RevisionDesignInput((), (), (), DBML, instruction)))

    assert result.question == question
    assert result.options == tuple(options)


@pytest.mark.asyncio
async def test_clear_requirement_continues_without_question() -> None:
    model = _model()
    model.results[DwConversationResult] = DwConversationResult(
        kind="proposal",
        question=None,
        options=[],
        allow_custom_answer=False,
        reason=None,
        dbml=DBML,
        summary="Đã cập nhật grain một giao dịch theo tháng.",
    )
    agent = DataWarehouseDesignAgent(model, PiiGuard(enabled=False))

    result = await agent.converse(
        _conversation_input(RevisionDesignInput((), (), (), DBML, "Doanh thu SUM theo tháng, grain một giao dịch"))
    )

    assert result.kind.value == "proposal"
    assert result.question is None


class FakeStructuredModel:
    """Runnable ghi nhận đúng một ainvoke cho schema được chọn."""

    def __init__(self, owner: "FakeChatModel", schema: type) -> None:
        self._owner = owner
        self._schema = schema

    async def ainvoke(self, messages: Any) -> Any:
        """Trả fixture và ghi prompt."""
        self._owner.calls.append(self._schema)
        self._owner.prompts.append(messages[-1].content)
        result = self._owner.results[self._schema]
        if isinstance(result, list):
            result = result.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class FakeChatModel:
    """Chat model giả lập hỗ trợ structured output."""

    def __init__(self, results: dict[type, object]) -> None:
        self.results = results
        self.calls: list[type] = []
        self.prompts: list[str] = []

    def with_structured_output(self, schema: type) -> FakeStructuredModel:
        """Trả runnable cho output schema."""
        return FakeStructuredModel(self, schema)


def _model() -> FakeChatModel:
    """Dựng model có fixture cho mọi Agent operation."""
    requirement_id = str(uuid4())
    return FakeChatModel(
        {
            RequirementClarificationResult: RequirementClarificationResult(
                requirements=[
                    GeneratedRequirementItem(
                        title="Theo dõi doanh thu",
                        description="Phân tích doanh thu theo tháng.",
                        requirement_type="ANALYTICAL",
                        priority="HIGH",
                        existing_requirement_id=None,
                    )
                ],
                status="READY",
                summary="Requirements are ready.",
            ),
            AnalyticalRequirementResult: AnalyticalRequirementResult(
                outcomes=[
                    AnalyticalDerivationOutcome(
                        source_requirement_id=requirement_id,
                        status="READY",
                        analytical_requirements=[
                            AnalyticalRequirementItem(
                                source_requirement_id=requirement_id,
                                metric="doanh thu",
                                dimension="tháng",
                                time_granularity="MONTH",
                                aggregation_method="SUM",
                                grain="Một giao dịch",
                            )
                        ],
                    )
                ]
            ),
            DbmlRevisionResult: DbmlRevisionResult(dbml=DBML),
        }
    )


@pytest.mark.asyncio
async def test_each_requirement_operation_invokes_llm_once() -> None:
    """Hai operation độc lập tạo đúng hai LLM invocations."""
    model = _model()
    agent = RequirementAnalysisAgent(model, PiiGuard(enabled=False))
    memory = ConversationMemory(
        None,
        (),
        "Analyze saved requirement context.",
        ConversationInputKind.USER_MESSAGE,
    )
    await agent.clarify_requirements(ClarifyRequirementsInput("Theo dõi doanh thu", (), (), memory))
    outcome = model.results[AnalyticalRequirementResult].outcomes[0]
    source_id = outcome.source_requirement_id
    requirement = RequirementContext(uuid4(), "Theo dõi doanh thu", "Theo tháng", "ANALYTICAL", "HIGH")
    outcome.source_requirement_id = str(requirement.id)
    outcome.analytical_requirements[0].source_requirement_id = str(requirement.id)
    await agent.derive_analytical_requirements(DeriveAnalyticalRequirementsInput((requirement,), ()))
    assert source_id != str(requirement.id)
    assert model.calls == [RequirementClarificationResult, AnalyticalRequirementResult]


@pytest.mark.asyncio
async def test_analytical_agent_rejects_missing_requirement_outcome() -> None:
    """Adapter bắt buộc output bao phủ đúng toàn bộ input IDs."""
    model = _model()
    outcome = model.results[AnalyticalRequirementResult].outcomes[0]
    first = RequirementContext(uuid4(), "Revenue", "Sum revenue", "ANALYTICAL", "HIGH")
    second = RequirementContext(uuid4(), "Privacy", "Mask sensitive data", "TECHNICAL", "HIGH")
    outcome.source_requirement_id = str(first.id)
    outcome.analytical_requirements[0].source_requirement_id = str(first.id)
    agent = RequirementAnalysisAgent(model, PiiGuard(enabled=False))

    with pytest.raises(InfrastructureException) as raised:
        await agent.derive_analytical_requirements(DeriveAnalyticalRequirementsInput((first, second), ()))

    assert raised.value.code is ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR


@pytest.mark.asyncio
async def test_design_operations_receive_parser_schema_and_call_once() -> None:
    """Generate/revise dùng SchemaMetadata thật và mỗi method gọi một lần."""
    model = _model()
    source = DataSource(
        project_id=uuid4(),
        name="rides",
        location="rides.csv",
        schema_metadata=SchemaMetadata(tables=(TableMetadata("rides", (ColumnMetadata("ride_id", "INTEGER"),)),)),
    )
    requirement = Requirement(project_id=source.project_id, title="Revenue", description="By month")
    agent = DataWarehouseDesignAgent(model, PiiGuard(enabled=False))
    await agent.generate(DataWarehouseDesignInput((requirement,), (), (source,)))
    await agent.revise(RevisionDesignInput((requirement,), (), (source,), DBML, "Add dimension"))
    assert model.calls == [DbmlRevisionResult, DbmlRevisionResult]
    assert all("ride_id" in prompt for prompt in model.prompts)


@pytest.mark.asyncio
async def test_conversation_retries_once_after_invalid_structured_output() -> None:
    """Chat tự sửa một lần khi provider bỏ sót DBML của proposal."""
    model = _model()
    model.results[DwConversationResult] = [
        ValueError("validation error: proposal requires dbml"),
        DwConversationResult(
            kind="proposal",
            question=None,
            options=[],
            allow_custom_answer=False,
            reason=None,
            dbml=DBML,
            summary="Đã cập nhật mô hình.",
        ),
    ]
    agent = DataWarehouseDesignAgent(model, PiiGuard(enabled=False))
    revision = RevisionDesignInput((), (), (), DBML, "Add relationships")

    result = await agent.converse(_conversation_input(revision))

    assert result.dbml == DBML
    assert model.calls == [DwConversationResult, DwConversationResult]
    assert "Output contract correction" in model.prompts[-1]


def test_agent_package_contains_no_langgraph_or_source_agent() -> None:
    """Legacy graph và SourceDataAgent đã bị xóa khỏi production package."""
    from pathlib import Path

    sources = "\n".join(
        path.read_text(encoding="utf-8") for path in Path("backend/src/infrastructure/agents").rglob("*.py")
    )
    assert "langgraph" not in sources.casefold()
    assert "SourceDataAgent" not in sources
