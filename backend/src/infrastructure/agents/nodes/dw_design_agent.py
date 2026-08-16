"""Node DWDesignAgent: thiết kế mô hình kho dữ liệu dạng DBML (data_flow.md Bước 3).

Đây cũng là ranh giới PII Guard hoạt động theo `data_flow.md` §2.4: dữ liệu được che ngay
trước khi gửi sang LLM API và hoàn nguyên ngay khi nhận kết quả về.
"""

import json

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.agents.prompts.dw_design import (
    DW_DESIGN_RETRY_PROMPT,
    DW_DESIGN_SYSTEM_PROMPT,
    DW_DESIGN_USER_PROMPT,
)
from src.infrastructure.agents.state import DwPipelineState
from src.infrastructure.llm.models import (
    AnalyticalRequirementItem,
    DbmlRevisionResult,
    SourceSchemaResult,
)
from src.infrastructure.security.pii_guard import PiiGuard

logger = get_logger(__name__)


def build_design_node(chat_model: BaseChatModel, pii_guard: PiiGuard):
    """Tạo node DWDesignAgent gắn với một Chat Model và bộ che PII cụ thể."""
    structured_model = chat_model.with_structured_output(DbmlRevisionResult)

    async def design_node(state: DwPipelineState) -> DwPipelineState:
        """Che PII, gọi LLM thiết kế mô hình DBML, rồi hoàn nguyên tên cột gốc."""
        attempts = state.get("attempts", 0) + 1

        rendered_schema = _render_schema(state.get("analyzed_schema"))
        rendered_requirements = _render_analytical(state.get("analytical_requirements", []))
        masked = pii_guard.mask_identifiers(rendered_schema + "\n" + rendered_requirements)

        logger.info(
            "dw_design_agent_invoked attempt=%d masked_fields=%d",
            attempts,
            masked.masked_count,
        )
        try:
            result = await structured_model.ainvoke(_build_messages(masked.text, state))
        except Exception as exc:
            logger.exception("DWDesignAgent gọi mô hình ngôn ngữ thất bại ở lượt %d.", attempts)
            raise InfrastructureException(
                code=ErrorCode.LLM_ERROR,
                message="Không nhận được phản hồi hợp lệ từ mô hình ngôn ngữ.",
            ) from exc

        # `dbml` là dữ liệu cấu trúc nên phải hoàn nguyên trọn vẹn — phần kiểm tra mã còn
        # sót do `validate_node` đảm nhiệm. `summary` chỉ là văn bản hiển thị nên chấp nhận
        # hoàn nguyên ở mức cố gắng hết sức.
        return {
            "proposed_dbml": pii_guard.unmask(result.dbml, masked.mapping),
            "summary": pii_guard.unmask(result.summary, masked.mapping),
            "attempts": attempts,
            "validation_error": "",
        }

    return design_node


def _build_messages(masked_context: str, state: DwPipelineState) -> list[SystemMessage | HumanMessage]:
    """Dựng danh sách message gửi cho LLM, bổ sung phần sửa lỗi khi đang retry."""
    user_prompt = DW_DESIGN_USER_PROMPT.format(
        analyzed_schema=masked_context,
        analytical_requirements="(đã gộp ở phần trên)",
    )

    validation_error = state.get("validation_error", "")
    if validation_error:
        user_prompt += "\n" + DW_DESIGN_RETRY_PROMPT.format(validation_error=validation_error)

    return [
        SystemMessage(content=DW_DESIGN_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]


def _render_schema(schema: SourceSchemaResult | None) -> str:
    """Dựng đoạn văn bản mô tả cấu trúc nguồn dữ liệu đã phân tích."""
    if schema is None or not schema.tables:
        return "## Cấu trúc nguồn\n(Chưa phân tích được cấu trúc nguồn dữ liệu.)"
    return "## Cấu trúc nguồn\n" + json.dumps(
        schema.model_dump(), ensure_ascii=False, indent=2
    )


def _render_analytical(items: list[AnalyticalRequirementItem]) -> str:
    """Dựng đoạn văn bản mô tả danh sách yêu cầu phân tích."""
    if not items:
        return "## Yêu cầu phân tích\n(Chưa rút trích được yêu cầu phân tích nào.)"
    payload = [item.model_dump() for item in items]
    return "## Yêu cầu phân tích\n" + json.dumps(payload, ensure_ascii=False, indent=2)
