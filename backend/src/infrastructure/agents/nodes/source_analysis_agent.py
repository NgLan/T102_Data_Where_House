"""Node SourceDataAgent: phân tích cấu trúc nguồn dữ liệu thô (data_flow.md Bước 2).

PII Guard chặn ngay tại ranh giới gọi LLM: mô tả nguồn dữ liệu có thể chứa tên cột nhạy cảm
và cả giá trị cá nhân do người dùng gõ tay.
"""

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.agents.prompts.source_analysis import (
    SOURCE_ANALYSIS_SYSTEM_PROMPT,
    SOURCE_ANALYSIS_USER_PROMPT,
)
from src.infrastructure.agents.state import DwPipelineState
from src.infrastructure.llm.models import SourceSchemaResult
from src.infrastructure.security.pii_guard import PiiGuard

logger = get_logger(__name__)


def build_source_analysis_node(chat_model: BaseChatModel, pii_guard: PiiGuard):
    """Tạo node SourceDataAgent gắn với một Chat Model và bộ che PII cụ thể."""
    structured_model = chat_model.with_structured_output(SourceSchemaResult)

    async def source_analysis_node(state: DwPipelineState) -> DwPipelineState:
        """Đọc mô tả nguồn dữ liệu và suy ra cấu trúc bảng/cột/quan hệ."""
        rendered = _render_data_sources(state.get("raw_data_sources", []))
        masked = pii_guard.mask_identifiers(rendered)
        masked_text = pii_guard.mask_free_text(masked.text)

        logger.info(
            "source_data_agent_invoked sources=%d masked_fields=%d",
            len(state.get("raw_data_sources", [])),
            masked.masked_count,
        )
        try:
            result = await structured_model.ainvoke(
                [
                    SystemMessage(content=SOURCE_ANALYSIS_SYSTEM_PROMPT),
                    HumanMessage(
                        content=SOURCE_ANALYSIS_USER_PROMPT.format(data_sources=masked_text)
                    ),
                ]
            )
        except Exception as exc:
            logger.exception("SourceDataAgent gọi mô hình ngôn ngữ thất bại.")
            raise InfrastructureException(
                code=ErrorCode.LLM_ERROR,
                message="Không phân tích được cấu trúc nguồn dữ liệu.",
            ) from exc

        restored = _unmask_schema(result, pii_guard, masked.mapping)
        logger.info("source_data_agent_completed tables=%d", len(restored.tables))
        return {"analyzed_schema": restored}

    return source_analysis_node


def _render_data_sources(data_sources: list[dict[str, str]]) -> str:
    """Dựng đoạn văn bản mô tả toàn bộ nguồn dữ liệu để đưa vào prompt."""
    if not data_sources:
        return "(Dự án chưa khai báo nguồn dữ liệu nào.)"

    blocks: list[str] = []
    for index, source in enumerate(data_sources, start=1):
        blocks.append(
            f"### Nguồn {index}: {source.get('name', '')}\n"
            f"- Định dạng: {source.get('type', '')}\n"
            f"- Vị trí: {source.get('location', '')}\n"
            f"- Mô tả: {source.get('description') or '(không có mô tả)'}"
        )
    return "\n\n".join(blocks)


def _unmask_schema(
    result: SourceSchemaResult, pii_guard: PiiGuard, mapping: dict[str, str]
) -> SourceSchemaResult:
    """Hoàn nguyên tên cột gốc trong toàn bộ kết quả phân tích."""
    if not mapping:
        return result

    for table in result.tables:
        table.name = pii_guard.unmask(table.name, mapping)
        for column in table.columns:
            column.name = pii_guard.unmask(column.name, mapping)
            if column.foreign_key_reference:
                column.foreign_key_reference = pii_guard.unmask(
                    column.foreign_key_reference, mapping
                )
    for relationship in result.relationships:
        relationship.from_column = pii_guard.unmask(relationship.from_column, mapping)
        relationship.to_column = pii_guard.unmask(relationship.to_column, mapping)
    result.summary = pii_guard.unmask(result.summary, mapping)
    return result
