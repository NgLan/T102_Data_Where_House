"""Adapter nối cổng IDataModelGenerator của tầng Domain với pipeline LangGraph."""

from langchain_core.language_models import BaseChatModel
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.logging import get_logger
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import AggregationMethod
from src.domain.data_model.generation import DbmlGenerationResult, IDataModelGenerator
from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import RelationshipType
from src.domain.data_source.value_objects import (
    ColumnMetadata,
    RelationshipMetadata,
    SchemaMetadata,
    TableMetadata,
)
from src.domain.requirement.entities import Requirement
from src.infrastructure.agents.state import DwPipelineState
from src.infrastructure.agents.workflows.dw_design import build_dw_pipeline_graph
from src.infrastructure.llm.models import (
    AnalyticalRequirementItem,
    SourceSchemaResult,
)
from src.infrastructure.security.pii_guard import PiiGuard

logger = get_logger(__name__)


class LangGraphDataModelGenerator(IDataModelGenerator):
    """Sinh mô hình dữ liệu bằng pipeline 4 agent trên LangGraph."""

    def __init__(self, chat_model: BaseChatModel, pii_guard: PiiGuard) -> None:
        """Khởi tạo adapter và biên dịch sẵn đồ thị."""
        self._graph = build_dw_pipeline_graph(chat_model, pii_guard)

    async def generate(
        self,
        requirements: list[Requirement],
        data_sources: list[DataSource],
    ) -> DbmlGenerationResult:
        """Chạy pipeline 4 agent để sinh mô hình DBML từ yêu cầu và nguồn dữ liệu."""
        initial_state: DwPipelineState = {
            "raw_requirements": [_requirement_to_dict(item) for item in requirements],
            "raw_data_sources": [_data_source_to_dict(item) for item in data_sources],
            "attempts": 0,
            "validation_error": "",
        }

        final_state: DwPipelineState = await self._graph.ainvoke(initial_state)

        validation_error = final_state.get("validation_error", "")
        if validation_error:
            logger.error(
                "dbml_generation_failed attempts=%d error=%s",
                final_state.get("attempts", 0),
                validation_error,
            )
            raise BusinessException(
                code=ErrorCode.INVALID_DBML_CONTENT,
                message=(
                    "AI Agent không sinh được mô hình DBML hợp lệ sau "
                    f"{final_state.get('attempts', 0)} lần thử. "
                    "Vui lòng bổ sung mô tả nguồn dữ liệu rõ ràng hơn."
                ),
            )

        logger.info(
            "dbml_generation_completed attempts=%d", final_state.get("attempts", 0)
        )
        return DbmlGenerationResult(
            dbml=final_state["proposed_dbml"],
            summary=final_state.get("summary", ""),
            analyzed_schema=_to_schema_metadata(final_state.get("analyzed_schema")),
            analytical_requirements=_to_analytical_entities(
                final_state.get("analytical_requirements", []), requirements
            ),
            attempts=final_state.get("attempts", 0),
        )


def _requirement_to_dict(requirement: Requirement) -> dict[str, str]:
    """Rút gọn Requirement thành dữ liệu thô cho prompt."""
    return {
        "title": requirement.title,
        "description": requirement.description,
        "type": str(requirement.type),
        "priority": str(requirement.priority),
    }


def _data_source_to_dict(data_source: DataSource) -> dict[str, str]:
    """Rút gọn DataSource thành dữ liệu thô cho prompt."""
    return {
        "name": data_source.name,
        "type": str(data_source.type),
        "location": data_source.location,
        "description": data_source.description or "",
    }


def _to_schema_metadata(result: SourceSchemaResult | None) -> SchemaMetadata:
    """Ánh xạ kết quả LLM sang Value Object SchemaMetadata của tầng Domain."""
    if result is None:
        return SchemaMetadata()

    tables = tuple(
        TableMetadata(
            name=table.name,
            columns=tuple(
                ColumnMetadata(
                    name=column.name,
                    data_type=column.data_type,
                    primary_key=column.primary_key,
                    nullable=column.nullable,
                    unique=column.unique,
                    foreign_key_reference=column.foreign_key_reference,
                    description=column.description,
                )
                for column in table.columns
            ),
        )
        for table in result.tables
    )
    relationships = tuple(
        RelationshipMetadata(
            from_column=item.from_column,
            to_column=item.to_column,
            type=_parse_relationship_type(item.type),
        )
        for item in result.relationships
    )
    return SchemaMetadata(tables=tables, relationships=relationships)


def _parse_relationship_type(value: str) -> RelationshipType:
    """Chuyển chuỗi LLM trả về thành enum, quay về mặc định nếu không hợp lệ.

    Prompt yêu cầu LLM trả chữ HOA cho dễ đọc, còn enum của domain lưu chữ thường,
    nên phải chuẩn hóa trước khi ánh xạ.
    """
    try:
        return RelationshipType(value.strip().lower())
    except ValueError:
        logger.warning("relationship_type_unrecognised value=%s", value)
        return RelationshipType.MANY_TO_ONE


def _to_analytical_entities(
    items: list[AnalyticalRequirementItem],
    requirements: list[Requirement],
) -> tuple[AnalyticalRequirement, ...]:
    """Ánh xạ kết quả LLM sang thực thể AnalyticalRequirement, nối về yêu cầu gốc."""
    title_to_id = {item.title: item.id for item in requirements}
    fallback_id = requirements[0].id if requirements else None

    entities: list[AnalyticalRequirement] = []
    for item in items:
        requirement_id = title_to_id.get(item.source_requirement_title, fallback_id)
        if requirement_id is None:
            logger.warning("analytical_requirement_skipped metric=%s", item.metric)
            continue
        entities.append(
            AnalyticalRequirement(
                requirement_id=requirement_id,
                metric=item.metric,
                dimension=item.dimension,
                time_granularity=item.time_granularity,
                aggregation_method=_parse_aggregation(item.aggregation_method),
                grain=item.grain,
            )
        )
    return tuple(entities)


def _parse_aggregation(value: str) -> AggregationMethod | None:
    """Chuyển chuỗi LLM trả về thành enum AggregationMethod."""
    try:
        return AggregationMethod(value.upper())
    except ValueError:
        logger.warning("aggregation_method_unrecognised value=%s", value)
        return None
