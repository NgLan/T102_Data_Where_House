"""Unit tests cho Agent operation không dùng graph hoặc tool loop."""

from typing import Any
from uuid import uuid4

import pytest
from langchain_core.messages import AIMessage
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
    EvaluateSourceCoverageInput,
    RequirementContext,
)
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.analytical_requirement.entities import AnalyticalRequirement
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
from src.infrastructure.llm.source_coverage_structured_outputs import SourceCoverageLlmResult
from src.infrastructure.security.pii_guard import PiiGuard

DBML = "Table Fact_Rides {\n  ride_key int [pk]\n}"


class OutputParserError(ValueError):
    """Mô phỏng lỗi parser chính thức thay vì ValueError message fallback."""


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


def test_requirement_clarification_summary_defaults_to_empty_string() -> None:
    result = RequirementClarificationResult(
        requirements=[
            GeneratedRequirementItem(
                title="Revenue",
                description="Monthly revenue.",
                requirement_type="ANALYTICAL",
                priority="HIGH",
                existing_requirement_ref=None,
            )
        ],
        status="NEEDS_CLARIFICATION",
        question="Which metric?",
        options=["Revenue", "Orders"],
        allow_custom_answer=True,
        reason="Metric is unclear.",
    )

    assert result.summary == ""


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

    def __init__(self, owner: "FakeChatModel", schema: type, include_raw: bool) -> None:
        self._owner = owner
        self._schema = schema
        self._include_raw = include_raw

    async def ainvoke(self, messages: Any) -> Any:
        """Trả fixture và ghi prompt."""
        self._owner.calls.append(self._schema)
        self._owner.prompts.append(messages[-1].content)
        result = self._owner.results[self._schema]
        if isinstance(result, list):
            result = result.pop(0)
        if isinstance(result, Exception):
            raise result
        if self._include_raw:
            if isinstance(result, AIMessage):
                return {"raw": result, "parsed": None, "parsing_error": "invalid item"}
            raw = AIMessage(
                content=result.model_dump_json(),
                response_metadata={"finish_reason": "stop", "model_name": "fake"},
            )
            return {"raw": raw, "parsed": result, "parsing_error": None}
        return result


class FakeChatModel:
    """Chat model giả lập hỗ trợ structured output."""

    def __init__(self, results: dict[type, object]) -> None:
        self.results = results
        self.calls: list[type] = []
        self.prompts: list[str] = []

    def with_structured_output(
        self,
        schema: type,
        *,
        include_raw: bool = False,
    ) -> FakeStructuredModel:
        """Trả runnable cho output schema."""
        return FakeStructuredModel(self, schema, include_raw)


def _model() -> FakeChatModel:
    """Dựng model có fixture cho mọi Agent operation."""
    return FakeChatModel(
        {
            RequirementClarificationResult: RequirementClarificationResult(
                requirements=[
                    GeneratedRequirementItem(
                        title="Theo dõi doanh thu",
                        description="Phân tích doanh thu theo tháng.",
                        requirement_type="ANALYTICAL",
                        priority="HIGH",
                        existing_requirement_ref=None,
                    )
                ],
                status="READY",
                summary="Requirements are ready.",
            ),
            AnalyticalRequirementResult: AnalyticalRequirementResult(
                outcomes=[
                    AnalyticalDerivationOutcome(
                        requirement_ref="R1",
                        status="READY",
                        analytical_requirements=[
                            AnalyticalRequirementItem(
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
    requirement = RequirementContext(uuid4(), "Theo dõi doanh thu", "Theo tháng", "ANALYTICAL", "HIGH")
    result = await agent.derive_analytical_requirements(DeriveAnalyticalRequirementsInput((requirement,)))
    assert result.outcomes[0].source_requirement_id == requirement.id
    assert str(requirement.id) not in model.prompts[-1]
    assert model.calls == [RequirementClarificationResult, AnalyticalRequirementResult]


@pytest.mark.asyncio
async def test_markdown_clarification_is_recovered_without_retry() -> None:
    model = _model()
    typed = model.results[RequirementClarificationResult]
    assert isinstance(typed, RequirementClarificationResult)
    model.results[RequirementClarificationResult] = AIMessage(
        content=f"```json\n{typed.model_dump_json()}\n```",
        response_metadata={"finish_reason": "stop", "model_name": "fake"},
    )
    memory = ConversationMemory(
        None, (), "Analyze requirement.", ConversationInputKind.USER_MESSAGE
    )
    agent = RequirementAnalysisAgent(model, PiiGuard(enabled=False))

    result = await agent.clarify_requirements(
        ClarifyRequirementsInput("Monthly revenue", (), (), memory)
    )

    assert result.summary == "Requirements are ready."
    assert model.calls == [RequirementClarificationResult]


@pytest.mark.asyncio
async def test_provider_failure_does_not_consume_structured_retries() -> None:
    model = _model()
    model.results[AnalyticalRequirementResult] = RuntimeError("network unavailable")
    requirement = RequirementContext(
        uuid4(), "Revenue", "Monthly revenue", "ANALYTICAL", "HIGH"
    )
    agent = RequirementAnalysisAgent(model, PiiGuard(enabled=False))

    with pytest.raises(InfrastructureException) as raised:
        await agent.derive_analytical_requirements(
            DeriveAnalyticalRequirementsInput((requirement,))
        )

    assert raised.value.code is ErrorCode.LLM_ERROR
    assert model.calls == [AnalyticalRequirementResult]


@pytest.mark.asyncio
async def test_analytical_agent_rejects_missing_requirement_outcome() -> None:
    """Adapter bắt buộc output bao phủ đúng toàn bộ input IDs."""
    model = _model()
    first = RequirementContext(uuid4(), "Revenue", "Sum revenue", "ANALYTICAL", "HIGH")
    second = RequirementContext(uuid4(), "Privacy", "Mask sensitive data", "TECHNICAL", "HIGH")
    agent = RequirementAnalysisAgent(model, PiiGuard(enabled=False))

    with pytest.raises(InfrastructureException) as raised:
        await agent.derive_analytical_requirements(DeriveAnalyticalRequirementsInput((first, second)))

    assert raised.value.code is ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR


@pytest.mark.asyncio
async def test_analytical_retry_reuses_valid_outcomes() -> None:
    """Attempt sau chỉ nhận Requirement lỗi và merge theo input order."""
    model = _model()
    raw = AIMessage(
        content="""{"outcomes": [
            {"requirement_ref": "R1", "status": "NOT_ANALYTICAL",
             "analytical_requirements": [], "reason": "No analytical intent."},
            {"requirement_ref": "R2", "analytical_requirements": [], "reason": null}
        ]}""",
        response_metadata={"finish_reason": "stop", "model_name": "fake"},
    )
    corrected = AnalyticalRequirementResult(
        outcomes=[
            AnalyticalDerivationOutcome(
                requirement_ref="R2",
                status="NOT_ANALYTICAL",
                analytical_requirements=[],
                reason="No analytical intent.",
            )
        ]
    )
    model.results[AnalyticalRequirementResult] = [raw, corrected]
    requirements = (
        RequirementContext(uuid4(), "Privacy", "Mask data", "TECHNICAL", "HIGH"),
        RequirementContext(uuid4(), "Audit", "Track access", "TECHNICAL", "HIGH"),
    )
    agent = RequirementAnalysisAgent(model, PiiGuard(enabled=False))

    result = await agent.derive_analytical_requirements(DeriveAnalyticalRequirementsInput(requirements))

    assert tuple(item.source_requirement_id for item in result.outcomes) == tuple(item.id for item in requirements)
    assert '"requirement_ref": "R1"' not in model.prompts[1]
    assert '"requirement_ref": "R2"' in model.prompts[1]
    assert model.calls == [AnalyticalRequirementResult, AnalyticalRequirementResult]


@pytest.mark.asyncio
async def test_source_coverage_retry_reuses_grounded_outcomes() -> None:
    """Outcome đã grounded không xuất hiện trong attempt sửa column kế tiếp."""
    model = _model()
    model.results[SourceCoverageLlmResult] = [
        AIMessage(
            content=_source_coverage_json("invented_column", include_a1=True),
            response_metadata={"finish_reason": "stop", "model_name": "fake"},
        ),
        SourceCoverageLlmResult.model_validate(_source_coverage_payload("amount", include_a1=False)),
    ]
    project_id = uuid4()
    requirements = (
        RequirementContext(uuid4(), "Privacy", "Mask data", "TECHNICAL", "HIGH"),
        RequirementContext(uuid4(), "Revenue", "Sum amount", "ANALYTICAL", "HIGH"),
    )
    analytical = (
        AnalyticalRequirement(requirement_id=requirements[0].id, dimension="privacy"),
        AnalyticalRequirement(requirement_id=requirements[1].id, metric="revenue"),
    )
    source = DataSource(
        project_id=project_id,
        name="sales",
        location="sales.csv",
        schema_metadata=SchemaMetadata(tables=(TableMetadata("sales", (ColumnMetadata("amount", "DECIMAL"),)),)),
    )
    agent = RequirementAnalysisAgent(model, PiiGuard(enabled=False))

    result = await agent.evaluate_source_coverage(EvaluateSourceCoverageInput(requirements, analytical, (source,)))

    assert tuple(item.analytical_requirement_id for item in result.outcomes) == tuple(item.id for item in analytical)
    assert '"analytical_requirement_ref": "A1"' not in model.prompts[1]
    assert '"analytical_requirement_ref": "A2"' in model.prompts[1]


def _source_coverage_json(column_name: str, *, include_a1: bool) -> str:
    import json

    return json.dumps(_source_coverage_payload(column_name, include_a1=include_a1))


def _source_coverage_payload(
    column_name: str,
    *,
    include_a1: bool,
) -> dict[str, object]:
    outcomes: list[dict[str, object]] = []
    if include_a1:
        outcomes.append(
            {
                "analytical_requirement_ref": "A1",
                "assessments": [
                    {
                        "status": "MISSING_SOURCE",
                        "required_concept_key": "PRIVACY_POLICY",
                        "title": "Privacy policy",
                        "explanation": "No source evidence exists.",
                        "question": None,
                        "question_type": None,
                        "candidates": [],
                    }
                ],
            }
        )
    outcomes.append(
        {
            "analytical_requirement_ref": "A2",
            "assessments": [
                {
                    "status": "NEEDS_SOURCE_CONFIRMATION",
                    "required_concept_key": "REVENUE_AMOUNT",
                    "title": "Revenue amount",
                    "explanation": "Confirm the amount field.",
                    "question": "Does this field represent revenue?",
                    "question_type": "SINGLE_CANDIDATE_CONFIRMATION",
                    "candidates": [
                        {
                            "label": "Amount",
                            "references": [
                                {
                                    "kind": "COLUMN",
                                    "source_ref": "S1",
                                    "table_name": "sales",
                                    "column_name": column_name,
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    )
    return {"outcomes": outcomes}


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
        OutputParserError("proposal requires dbml"),
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
