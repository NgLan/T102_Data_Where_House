"""Kiểm thử pipeline 4 agent sinh mô hình dữ liệu (T-019).

Toàn bộ bài kiểm thử dùng Chat Model giả lập — KHÔNG gọi LLM thật, không tốn chi phí API.
"""

from typing import Any

import pytest
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.analytical_requirement.enums import AggregationMethod
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import DataSourceType, RelationshipType
from src.domain.requirement.entities import Requirement
from src.infrastructure.agents.constants import MAX_REVISION_ATTEMPTS
from src.infrastructure.agents.data_model_generator import LangGraphDataModelGenerator
from src.infrastructure.llm.models import (
    AnalyticalRequirementItem,
    AnalyticalRequirementResult,
    DbmlRevisionResult,
    SourceColumnItem,
    SourceRelationshipItem,
    SourceSchemaResult,
    SourceTableItem,
)
from src.infrastructure.security.pii_guard import PiiGuard

VALID_DBML = """Table Dim_Driver {
  driver_key int [pk]
  full_name varchar
}

Table Fact_Rides {
  ride_key int [pk]
  driver_key int [ref: > Dim_Driver.driver_key]
  fare_amount decimal
}"""

INVALID_DBML = "Table Dim_Driver { driver_key"


def _schema_result() -> SourceSchemaResult:
    """Kết quả giả lập của SourceDataAgent."""
    return SourceSchemaResult(
        tables=[
            SourceTableItem(
                name="rides",
                columns=[
                    SourceColumnItem(name="id", data_type="int", primary_key=True),
                    SourceColumnItem(
                        name="driver_id",
                        data_type="int",
                        foreign_key_reference="drivers.id",
                    ),
                    SourceColumnItem(name="fare_amount", data_type="decimal"),
                ],
            ),
            SourceTableItem(
                name="drivers",
                columns=[
                    SourceColumnItem(name="id", data_type="int", primary_key=True),
                    SourceColumnItem(name="phone_number", data_type="varchar"),
                ],
            ),
        ],
        relationships=[
            SourceRelationshipItem(
                from_column="rides.driver_id",
                to_column="drivers.id",
                type="MANY_TO_ONE",
            )
        ],
        summary="Hai bảng nguồn: chuyến đi và tài xế.",
    )


def _analytical_result(title: str = "Doanh thu theo tài xế") -> AnalyticalRequirementResult:
    """Kết quả giả lập của RequirementAgent."""
    return AnalyticalRequirementResult(
        analytical_requirements=[
            AnalyticalRequirementItem(
                metric="tổng doanh thu",
                dimension="theo tài xế",
                time_granularity="tháng",
                aggregation_method="SUM",
                grain="Mỗi dòng là một chuyến đi hoàn thành.",
                source_requirement_title=title,
            )
        ],
        summary="Rút trích 1 yêu cầu phân tích.",
    )


class FakeStructuredModel:
    """Runnable giả lập, trả kết quả theo đúng schema mà node yêu cầu."""

    def __init__(self, owner: "FakeChatModel", schema: Any) -> None:
        """Ghi nhớ Chat Model cha và schema đang được yêu cầu."""
        self._owner = owner
        self._schema = schema

    async def ainvoke(self, messages: Any, *args: Any, **kwargs: Any) -> Any:
        """Trả kết quả dựng sẵn tương ứng schema, đồng thời ghi lại prompt."""
        prompt = str(messages[-1].content)
        self._owner.received_prompts.append(prompt)

        if self._schema is SourceSchemaResult:
            self._owner.source_calls += 1
            return self._owner.schema_result
        if self._schema is AnalyticalRequirementResult:
            self._owner.requirement_calls += 1
            return self._owner.analytical_result

        index = min(self._owner.design_calls, len(self._owner.design_results) - 1)
        self._owner.design_calls += 1
        return self._owner.design_results[index]


class FakeChatModel:
    """Chat Model giả lập cho cả ba agent trong pipeline."""

    def __init__(
        self,
        design_results: list[DbmlRevisionResult],
        schema_result: SourceSchemaResult | None = None,
        analytical_result: AnalyticalRequirementResult | None = None,
    ) -> None:
        """Khởi tạo với kết quả dựng sẵn cho từng agent."""
        self.design_results = design_results
        self.schema_result = schema_result or _schema_result()
        self.analytical_result = analytical_result or _analytical_result()
        self.received_prompts: list[str] = []
        self.source_calls = 0
        self.requirement_calls = 0
        self.design_calls = 0

    def with_structured_output(self, schema: Any, **kwargs: Any) -> FakeStructuredModel:
        """Trả runnable giả lập gắn với schema được yêu cầu."""
        return FakeStructuredModel(self, schema)


@pytest.fixture
def requirements() -> list[Requirement]:
    """Yêu cầu nghiệp vụ thô dùng làm đầu vào pipeline."""
    return [
        Requirement(
            title="Doanh thu theo tài xế",
            description="Cần xem tổng doanh thu từng tài xế theo tháng.",
        )
    ]


@pytest.fixture
def data_sources() -> list[DataSource]:
    """Nguồn dữ liệu thô dùng làm đầu vào pipeline."""
    return [
        DataSource(
            name="rides_export",
            location="/data/rides.csv",
            type=DataSourceType.CSV,
            description="Bảng chuyến đi và bảng tài xế, có cột phone_number.",
        )
    ]


def _build_generator(
    chat_model: FakeChatModel, pii_enabled: bool = False
) -> LangGraphDataModelGenerator:
    """Dựng generator với bộ che PII bật/tắt theo nhu cầu từng bài kiểm thử."""
    return LangGraphDataModelGenerator(chat_model, PiiGuard(enabled=pii_enabled))


# --- Luồng thành công ---------------------------------------------------------


@pytest.mark.asyncio
async def test_pipeline_runs_all_three_agents_once(
    requirements: list[Requirement], data_sources: list[DataSource]
) -> None:
    """Pipeline gọi đủ SourceDataAgent, RequirementAgent và DWDesignAgent, mỗi con một lần."""
    chat_model = FakeChatModel([DbmlRevisionResult(dbml=VALID_DBML, summary="Đã thiết kế.")])
    generator = _build_generator(chat_model)

    result = await generator.generate(requirements, data_sources)

    assert chat_model.source_calls == 1
    assert chat_model.requirement_calls == 1
    assert chat_model.design_calls == 1
    assert result.dbml == VALID_DBML
    assert result.attempts == 1


@pytest.mark.asyncio
async def test_source_agent_output_maps_to_schema_metadata(
    requirements: list[Requirement], data_sources: list[DataSource]
) -> None:
    """Kết quả SourceDataAgent được ánh xạ đúng sang Value Object SchemaMetadata."""
    chat_model = FakeChatModel([DbmlRevisionResult(dbml=VALID_DBML, summary="ok")])
    generator = _build_generator(chat_model)

    result = await generator.generate(requirements, data_sources)

    schema = result.analyzed_schema
    assert [table.name for table in schema.tables] == ["rides", "drivers"]
    assert schema.tables[0].columns[0].primary_key is True
    assert schema.tables[0].columns[1].foreign_key_reference == "drivers.id"
    assert schema.relationships[0].type is RelationshipType.MANY_TO_ONE


@pytest.mark.asyncio
async def test_requirement_agent_output_maps_to_entities(
    requirements: list[Requirement], data_sources: list[DataSource]
) -> None:
    """Kết quả RequirementAgent được ánh xạ sang thực thể AnalyticalRequirement."""
    chat_model = FakeChatModel([DbmlRevisionResult(dbml=VALID_DBML, summary="ok")])
    generator = _build_generator(chat_model)

    result = await generator.generate(requirements, data_sources)

    assert len(result.analytical_requirements) == 1
    analytical = result.analytical_requirements[0]
    assert analytical.metric == "tổng doanh thu"
    assert analytical.aggregation_method is AggregationMethod.SUM
    assert analytical.requirement_id == requirements[0].id


@pytest.mark.asyncio
async def test_unknown_aggregation_method_becomes_none(
    requirements: list[Requirement], data_sources: list[DataSource]
) -> None:
    """Phương thức tổng hợp lạ không làm vỡ pipeline, chỉ để trống."""
    analytical = _analytical_result()
    analytical.analytical_requirements[0].aggregation_method = "MEDIAN"
    chat_model = FakeChatModel(
        [DbmlRevisionResult(dbml=VALID_DBML, summary="ok")], analytical_result=analytical
    )
    generator = _build_generator(chat_model)

    result = await generator.generate(requirements, data_sources)

    assert result.analytical_requirements[0].aggregation_method is None


# --- Thứ tự pipeline ----------------------------------------------------------


@pytest.mark.asyncio
async def test_requirement_agent_receives_analyzed_schema(
    requirements: list[Requirement], data_sources: list[DataSource]
) -> None:
    """RequirementAgent phải nhận được kết quả phân tích của SourceDataAgent.

    Đây là ràng buộc thứ tự trong `data_flow.md` Bước 2: SourceDataAgent đẩy kết quả sang
    RequirementAgent để tạo AnalyticalRequirement.
    """
    chat_model = FakeChatModel([DbmlRevisionResult(dbml=VALID_DBML, summary="ok")])
    generator = _build_generator(chat_model)

    await generator.generate(requirements, data_sources)

    requirement_prompt = chat_model.received_prompts[1]
    assert "rides" in requirement_prompt
    assert "drivers" in requirement_prompt
    assert "Doanh thu theo tài xế" in requirement_prompt


@pytest.mark.asyncio
async def test_design_agent_receives_both_schema_and_analytical(
    requirements: list[Requirement], data_sources: list[DataSource]
) -> None:
    """DWDesignAgent phải nhận cả cấu trúc nguồn lẫn yêu cầu phân tích."""
    chat_model = FakeChatModel([DbmlRevisionResult(dbml=VALID_DBML, summary="ok")])
    generator = _build_generator(chat_model)

    await generator.generate(requirements, data_sources)

    design_prompt = chat_model.received_prompts[2]
    assert "rides" in design_prompt
    assert "tổng doanh thu" in design_prompt


# --- Vòng lặp retry -----------------------------------------------------------


@pytest.mark.asyncio
async def test_invalid_dbml_triggers_retry(
    requirements: list[Requirement], data_sources: list[DataSource]
) -> None:
    """DBML sai cú pháp ở lượt đầu thì DWDesignAgent được gọi lại và lượt hai được chấp nhận."""
    chat_model = FakeChatModel(
        [
            DbmlRevisionResult(dbml=INVALID_DBML, summary="hỏng"),
            DbmlRevisionResult(dbml=VALID_DBML, summary="ok"),
        ]
    )
    generator = _build_generator(chat_model)

    result = await generator.generate(requirements, data_sources)

    assert result.dbml == VALID_DBML
    assert result.attempts == 2
    assert chat_model.design_calls == 2
    # Chỉ DWDesignAgent chạy lại, hai agent phía trước không bị gọi thừa
    assert chat_model.source_calls == 1
    assert chat_model.requirement_calls == 1


@pytest.mark.asyncio
async def test_pipeline_fails_after_exhausting_attempts(
    requirements: list[Requirement], data_sources: list[DataSource]
) -> None:
    """Sai cú pháp ở mọi lượt thì dừng đúng số lần cho phép và ném lỗi nghiệp vụ."""
    chat_model = FakeChatModel([DbmlRevisionResult(dbml=INVALID_DBML, summary="hỏng")])
    generator = _build_generator(chat_model)

    with pytest.raises(BusinessException) as exc_info:
        await generator.generate(requirements, data_sources)

    assert exc_info.value.code == ErrorCode.INVALID_DBML_CONTENT
    assert chat_model.design_calls == MAX_REVISION_ATTEMPTS


# --- PII Guard (FR6.2) --------------------------------------------------------


@pytest.mark.asyncio
async def test_pii_is_masked_before_reaching_every_agent(
    requirements: list[Requirement], data_sources: list[DataSource]
) -> None:
    """Tên cột nhạy cảm trong mô tả nguồn không được lọt vào prompt của bất kỳ agent nào."""
    chat_model = FakeChatModel([DbmlRevisionResult(dbml=VALID_DBML, summary="ok")])
    generator = _build_generator(chat_model, pii_enabled=True)

    await generator.generate(requirements, data_sources)

    # Mô tả nguồn có 'phone_number'; prompt của SourceDataAgent phải đã che nó đi
    assert "phone_number" not in chat_model.received_prompts[0]


@pytest.mark.asyncio
async def test_renamed_placeholder_fails_closed(
    requirements: list[Requirement], data_sources: list[DataSource]
) -> None:
    """LLM tự đổi mã ẩn danh thì pipeline phải từ chối, không lưu DBML bẩn."""
    corrupted = VALID_DBML.replace("full_name varchar", "pii_field_1 varchar")
    chat_model = FakeChatModel([DbmlRevisionResult(dbml=corrupted, summary="ok")])
    generator = _build_generator(chat_model, pii_enabled=True)

    with pytest.raises(BusinessException) as exc_info:
        await generator.generate(requirements, data_sources)

    assert exc_info.value.code == ErrorCode.INVALID_DBML_CONTENT
