"""Ranh giới gọi structured LLM dùng chung, có bảo vệ PII và dịch lỗi."""

from dataclasses import dataclass
from typing import TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.llm.exception_translator import translate_llm_failure
from src.infrastructure.llm.failure_classifier import LlmFailureClassifier
from src.infrastructure.llm.lazy_chat_model import StructuredChatModel, StructuredModel
from src.infrastructure.security.pii_guard import PiiGuard

StructuredOutput = TypeVar("StructuredOutput", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class RestoreContext:
    """Context hoàn nguyên PII cho structured output."""

    mapping: dict[str, str]
    pii_guard: PiiGuard


class StructuredLlmInvoker:
    """Thực hiện đúng một network invocation cho mỗi Agent operation."""

    def __init__(self, chat_model: StructuredChatModel, pii_guard: PiiGuard) -> None:
        self._chat_model = chat_model
        self._pii_guard = pii_guard

    async def invoke(
        self,
        system_prompt: str,
        user_prompt: str,
        output_type: type[StructuredOutput],
    ) -> StructuredOutput:
        """Che PII, gọi LLM một lần và hoàn nguyên structured output.

        Raises:
            InfrastructureException: Khi provider hoặc structured parsing thất bại.
        """
        masked = self._pii_guard.mask_identifiers(user_prompt)
        protected_prompt = self._pii_guard.mask_free_text(masked.text)
        structured_model = self._chat_model.with_structured_output(output_type)
        result = await _invoke_model(structured_model, system_prompt, protected_prompt)
        context = RestoreContext(masked.mapping, self._pii_guard)
        restored = _restore_model(result, output_type, context)
        _ensure_no_residual_placeholder(restored, self._pii_guard)
        return restored


async def _invoke_model(
    structured_model: StructuredModel, system_prompt: str, protected_prompt: str
) -> BaseModel:
    """Gọi provider đúng một lần và dịch technical exception."""
    try:
        return await structured_model.ainvoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=protected_prompt)]
        )
    except InfrastructureException:
        raise
    except Exception as exc:  # Provider SDK không có exception base chung.
        decision = LlmFailureClassifier().classify(exc)
        raise translate_llm_failure(decision) from exc


def _ensure_no_residual_placeholder(result: BaseModel, pii_guard: PiiGuard) -> None:
    """Fail closed nếu structured output còn mã PII bị biến dạng."""
    if pii_guard.has_residual_placeholder(result.model_dump_json()):
        raise InfrastructureException(
            ErrorCode.LLM_PII_DEGRADATION_ERROR,
            "Mô hình ngôn ngữ làm biến dạng mã ẩn danh PII.",
        )


def _restore_model(
    result: BaseModel,
    output_type: type[StructuredOutput],
    context: RestoreContext,
) -> StructuredOutput:
    """Hoàn nguyên mọi string field trong Pydantic output."""
    payload = _restore_value(result.model_dump(), context)
    return output_type.model_validate(payload)


def _restore_value(value: object, context: RestoreContext) -> object:
    """Duyệt cấu trúc JSON để hoàn nguyên placeholder identifier."""
    if isinstance(value, str):
        return context.pii_guard.unmask(value, context.mapping)
    if isinstance(value, list):
        return [_restore_value(item, context) for item in value]
    if isinstance(value, dict):
        return {key: _restore_value(item, context) for key, item in value.items()}
    return value
