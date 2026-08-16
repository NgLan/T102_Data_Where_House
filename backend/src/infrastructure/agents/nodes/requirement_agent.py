"""Node RequirementAgent: rút trích yêu cầu phân tích (data_flow.md Bước 2).

Theo `data_flow.md`, RequirementAgent nhận `Source Data đã được phân tích` từ SourceDataAgent
để tạo ra `AnalyticalRequirement`, nên node này luôn chạy SAU node phân tích nguồn dữ liệu.
"""

import json

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.agents.prompts.requirement import (
    REQUIREMENT_ANALYSIS_SYSTEM_PROMPT,
    REQUIREMENT_ANALYSIS_USER_PROMPT,
)
from src.infrastructure.agents.state import DwPipelineState
from src.infrastructure.llm.models import AnalyticalRequirementResult, SourceSchemaResult
from src.infrastructure.security.pii_guard import PiiGuard

logger = get_logger(__name__)


def build_requirement_analysis_node(chat_model: BaseChatModel, pii_guard: PiiGuard):
    """Tạo node RequirementAgent gắn với một Chat Model và bộ che PII cụ thể."""
    structured_model = chat_model.with_structured_output(AnalyticalRequirementResult)

    async def requirement_analysis_node(state: DwPipelineState) -> DwPipelineState:
        """Rút trích danh sách yêu cầu phân tích từ yêu cầu nghiệp vụ thô."""
        rendered_requirements = _render_requirements(state.get("raw_requirements", []))
        rendered_schema = _render_schema(state.get("analyzed_schema"))

        masked = pii_guard.mask_identifiers(rendered_schema)
        masked_requirements = pii_guard.mask_free_text(rendered_requirements)

        logger.info(
            "requirement_agent_invoked requirements=%d masked_fields=%d",
            len(state.get("raw_requirements", [])),
            masked.masked_count,
        )
        try:
            result = await structured_model.ainvoke(
                [
                    SystemMessage(content=REQUIREMENT_ANALYSIS_SYSTEM_PROMPT),
                    HumanMessage(
                        content=REQUIREMENT_ANALYSIS_USER_PROMPT.format(
                            requirements=masked_requirements,
                            analyzed_schema=masked.text,
                        )
                    ),
                ]
            )
        except Exception as exc:
            logger.exception("RequirementAgent gọi mô hình ngôn ngữ thất bại.")
            raise InfrastructureException(
                code=ErrorCode.LLM_ERROR,
                message="Không rút trích được yêu cầu phân tích.",
            ) from exc

        items = result.analytical_requirements
        for item in items:
            item.metric = pii_guard.unmask(item.metric, masked.mapping)
            item.dimension = pii_guard.unmask(item.dimension, masked.mapping)
            item.grain = pii_guard.unmask(item.grain, masked.mapping)

        logger.info("requirement_agent_completed analytical_requirements=%d", len(items))
        return {"analytical_requirements": items}

    return requirement_analysis_node


def _render_requirements(requirements: list[dict[str, str]]) -> str:
    """Dựng đoạn văn bản mô tả toàn bộ yêu cầu nghiệp vụ thô."""
    if not requirements:
        return "(Dự án chưa khai báo yêu cầu nghiệp vụ nào.)"

    blocks: list[str] = []
    for index, item in enumerate(requirements, start=1):
        blocks.append(
            f"### Yêu cầu {index}: {item.get('title', '')}\n"
            f"- Phân loại: {item.get('type', '')}\n"
            f"- Ưu tiên: {item.get('priority', '')}\n"
            f"- Mô tả: {item.get('description', '')}"
        )
    return "\n\n".join(blocks)


def _render_schema(schema: SourceSchemaResult | None) -> str:
    """Dựng đoạn văn bản mô tả cấu trúc nguồn dữ liệu đã phân tích."""
    if schema is None or not schema.tables:
        return "(Chưa phân tích được cấu trúc nguồn dữ liệu.)"
    return json.dumps(schema.model_dump(), ensure_ascii=False, indent=2)
