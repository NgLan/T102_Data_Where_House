"""Node DWDesignAgent: sinh phiên bản DBML mới từ yêu cầu ngôn ngữ tự nhiên.

Đây cũng là ranh giới mà PII Guard hoạt động theo `data_flow.md` §2.4: dữ liệu được che
ngay trước khi gửi sang LLM API và hoàn nguyên ngay khi nhận kết quả về.
"""

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.agents.prompts.dw_design import (
    DW_DESIGN_RETRY_PROMPT,
    DW_DESIGN_REVISE_SYSTEM_PROMPT,
    DW_DESIGN_REVISE_USER_PROMPT,
)
from src.infrastructure.agents.state import DwDesignState
from src.infrastructure.llm.models import DbmlRevisionResult
from src.infrastructure.security.pii_guard import PiiGuard

logger = get_logger(__name__)


def build_design_node(chat_model: BaseChatModel, pii_guard: PiiGuard):
    """Tạo node DWDesignAgent gắn với một Chat Model và bộ che PII cụ thể.

    Trả về một hàm bất đồng bộ đúng chuẩn node của LangGraph: nhận state, trả về phần
    state cần cập nhật.
    """
    structured_model = chat_model.with_structured_output(DbmlRevisionResult)

    async def design_node(state: DwDesignState) -> DwDesignState:
        """Che PII, gọi LLM sinh DBML mới, rồi hoàn nguyên tên cột gốc."""
        attempts = state.get("attempts", 0) + 1

        # PII Guard (chiều đi): che tên cột nhạy cảm và giá trị PII trong câu lệnh.
        masked_schema = pii_guard.mask_schema(state.get("current_dbml", ""))
        masked_instruction = pii_guard.mask_free_text(state.get("instruction", ""))
        messages = _build_messages(masked_schema.text, masked_instruction, state)

        logger.info(
            "dw_design_agent_invoked attempt=%d masked_fields=%d",
            attempts,
            masked_schema.masked_count,
        )
        try:
            result = await structured_model.ainvoke(messages)
        except Exception as exc:
            logger.exception("Gọi mô hình ngôn ngữ thất bại ở lượt %d.", attempts)
            raise InfrastructureException(
                code=ErrorCode.LLM_ERROR,
                message="Không nhận được phản hồi hợp lệ từ mô hình ngôn ngữ.",
            ) from exc

        # PII Guard (chiều về): khôi phục tên cột gốc.
        # `dbml` là dữ liệu cấu trúc nên phải hoàn nguyên trọn vẹn — phần kiểm tra mã còn
        # sót do `validate_node` đảm nhiệm. `summary` chỉ là văn bản hiển thị nên chấp nhận
        # hoàn nguyên ở mức cố gắng hết sức.
        return {
            "proposed_dbml": pii_guard.unmask(result.dbml, masked_schema.mapping),
            "summary": pii_guard.unmask(result.summary, masked_schema.mapping),
            "changed_tables": result.changed_tables,
            "attempts": attempts,
            "validation_error": "",
        }

    return design_node


def _build_messages(
    masked_dbml: str, masked_instruction: str, state: DwDesignState
) -> list[SystemMessage | HumanMessage]:
    """Dựng danh sách message gửi cho LLM, bổ sung phần sửa lỗi khi đang retry."""
    user_prompt = DW_DESIGN_REVISE_USER_PROMPT.format(
        current_dbml=masked_dbml,
        instruction=masked_instruction,
    )

    validation_error = state.get("validation_error", "")
    if validation_error:
        user_prompt += "\n" + DW_DESIGN_RETRY_PROMPT.format(validation_error=validation_error)

    return [
        SystemMessage(content=DW_DESIGN_REVISE_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]
