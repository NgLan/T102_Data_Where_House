"""Unit tests cho Agent operation không dùng graph hoặc tool loop."""

from typing import Any
from uuid import uuid4

import pytest
from src.application.data_warehouse_workflows.input import (
    AnalyticalAnalysisInput,
    DataWarehouseDesignInput,
    RawRequirementAnalysisInput,
    RequirementContext,
    RevisionDesignInput,
)
from src.domain.data_source.entities import DataSource
from src.domain.data_source.value_objects import ColumnMetadata, SchemaMetadata, TableMetadata
from src.domain.requirement.entities import Requirement
from src.infrastructure.agents.data_warehouse_design_agent import DataWarehouseDesignAgent
from src.infrastructure.agents.requirement_analysis_agent import RequirementAnalysisAgent
from src.infrastructure.llm.agent_structured_outputs import (
    AnalyticalRequirementItem,
    AnalyticalRequirementResult,
    DbmlRevisionResult,
    GeneratedRequirementItem,
    RequirementStructureResult,
)
from src.infrastructure.security.pii_guard import PiiGuard

DBML = "Table Fact_Rides {\n  ride_key int [pk]\n}"


class FakeStructuredModel:
    """Runnable ghi nhận đúng một ainvoke cho schema được chọn."""

    def __init__(self, owner: "FakeChatModel", schema: type) -> None:
        self._owner = owner
        self._schema = schema

    async def ainvoke(self, messages: Any) -> Any:
        """Trả fixture và ghi prompt."""
        self._owner.calls.append(self._schema)
        self._owner.prompts.append(messages[-1].content)
        return self._owner.results[self._schema]


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
            RequirementStructureResult: RequirementStructureResult(
                requirements=[
                    GeneratedRequirementItem(
                        title="Theo dõi doanh thu",
                        description="Phân tích doanh thu theo tháng.",
                        requirement_type="ANALYTICAL",
                        priority="HIGH",
                    )
                ]
            ),
            AnalyticalRequirementResult: AnalyticalRequirementResult(
                analytical_requirements=[
                    AnalyticalRequirementItem(
                        source_requirement_id=requirement_id,
                        metric="doanh thu",
                        dimension="tháng",
                        time_granularity="MONTH",
                        aggregation_method="SUM",
                        grain="Một giao dịch",
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
    await agent.structure_raw_requirement(RawRequirementAnalysisInput("Theo dõi doanh thu"))
    source_id = model.results[AnalyticalRequirementResult].analytical_requirements[0].source_requirement_id
    requirement = RequirementContext(
        uuid4(), "Theo dõi doanh thu", "Theo tháng", "ANALYTICAL", "HIGH"
    )
    model.results[AnalyticalRequirementResult].analytical_requirements[0].source_requirement_id = str(
        requirement.id
    )
    await agent.derive_analytical_requirements(AnalyticalAnalysisInput((requirement,), ()))
    assert source_id != str(requirement.id)
    assert model.calls == [RequirementStructureResult, AnalyticalRequirementResult]


@pytest.mark.asyncio
async def test_design_operations_receive_parser_schema_and_call_once() -> None:
    """Generate/revise dùng SchemaMetadata thật và mỗi method gọi một lần."""
    model = _model()
    source = DataSource(
        project_id=uuid4(),
        name="rides",
        location="rides.csv",
        schema_metadata=SchemaMetadata(
            tables=(TableMetadata("rides", (ColumnMetadata("ride_id", "INTEGER"),)),)
        ),
    )
    requirement = Requirement(project_id=source.project_id, title="Revenue", description="By month")
    agent = DataWarehouseDesignAgent(model, PiiGuard(enabled=False))
    await agent.generate(DataWarehouseDesignInput((requirement,), (), (source,)))
    await agent.revise(
        RevisionDesignInput((requirement,), (), (source,), DBML, "Add dimension")
    )
    assert model.calls == [DbmlRevisionResult, DbmlRevisionResult]
    assert all("ride_id" in prompt for prompt in model.prompts)


def test_agent_package_contains_no_langgraph_or_source_agent() -> None:
    """Legacy graph và SourceDataAgent đã bị xóa khỏi production package."""
    from pathlib import Path

    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path("backend/src/infrastructure/agents").rglob("*.py")
    )
    assert "langgraph" not in sources.casefold()
    assert "SourceDataAgent" not in sources
