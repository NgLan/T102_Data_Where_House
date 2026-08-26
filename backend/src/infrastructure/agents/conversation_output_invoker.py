"""Khôi phục một lần khi LLM trả sai contract hội thoại thiết kế."""

from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.infrastructure.llm.agent_structured_outputs import DwConversationResult
from src.infrastructure.llm.lazy_chat_model import StructuredChatModel
from src.infrastructure.llm.structured_llm_invoker import StructuredLlmInvoker
from src.infrastructure.security.pii_guard import PiiGuard

logger = get_logger(__name__)

OUTPUT_REPAIR_INSTRUCTION = """## Output contract correction
Correct only the structured shape; preserve the original grounded decision and do not add business
semantics. Return all seven keys: kind, question, options, allow_custom_answer, reason, dbml,
summary. For proposal, clarification fields are empty and dbml contains complete revised raw DBML.
For no_change, clarification fields are empty and dbml is null. For clarification, dbml is null and
one question, one to four grounded options, custom answers, and a concrete reason are required. Keep
summary to one or two sentences."""


class ConversationOutputInvoker:
    """Gọi structured conversation và retry đúng một lần khi output sai schema."""

    def __init__(self, chat_model: StructuredChatModel, pii_guard: PiiGuard) -> None:
        self._invoker = StructuredLlmInvoker(chat_model, pii_guard)

    async def invoke(self, system_prompt: str, user_prompt: str) -> DwConversationResult:
        """Retry với contract sửa lỗi mà không đưa raw response hỏng vào prompt."""
        try:
            return await self._invoke(system_prompt, user_prompt)
        except InfrastructureException as exc:
            if exc.code is not ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR:
                raise
            logger.warning("Retrying invalid DW conversation structured output once.")
            repaired_prompt = f"{user_prompt}\n\n{OUTPUT_REPAIR_INSTRUCTION}"
            return await self._invoke(system_prompt, repaired_prompt)

    async def _invoke(self, system_prompt: str, user_prompt: str) -> DwConversationResult:
        return await self._invoker.invoke(
            system_prompt,
            user_prompt,
            DwConversationResult,
        )
