"""Ranh giới gọi structured LLM dùng chung, có bảo vệ PII và dịch lỗi."""

from typing import TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.llm.exception_translator import translate_llm_failure
from src.infrastructure.llm.failure_classifier import LlmFailureClassifier
from src.infrastructure.llm.lazy_chat_model import StructuredChatModel, StructuredModel
from src.infrastructure.llm.structured_output_decoder import is_truncated_finish
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputFailureCategory as Category,
)
from src.infrastructure.llm.structured_output_models import StructuredOutputIssue, StructuredPayloadResult
from src.infrastructure.llm.structured_output_restoration import (
    RestoreContext,
    decode_and_restore_payload,
    ensure_no_residual_placeholder,
    restore_model,
)
from src.infrastructure.llm.structured_raw_response import extract_metadata
from src.infrastructure.security.pii_guard import PiiGuard

StructuredOutput = TypeVar("StructuredOutput", bound=BaseModel)


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
        restored = restore_model(result, output_type, context)
        ensure_no_residual_placeholder(restored, self._pii_guard)
        return restored

    async def invoke_payload(
        self,
        system_prompt: str,
        user_prompt: str,
        output_type: type[StructuredOutput],
    ) -> StructuredPayloadResult:
        """Gọi native schema và trả payload phục hồi kèm diagnostics an toàn."""
        masked = self._pii_guard.mask_identifiers(user_prompt)
        protected = self._pii_guard.mask_free_text(masked.text)
        model = self._chat_model.with_structured_output(output_type, include_raw=True)
        result = await _invoke_raw_model(model, system_prompt, protected)
        raw, parsed = result.get("raw"), result.get("parsed")
        metadata = extract_metadata(raw)
        context = RestoreContext(masked.mapping, self._pii_guard)
        if is_truncated_finish(metadata.finish_reason):
            issue = StructuredOutputIssue(
                Category.OUTPUT_TRUNCATED,
                "Provider stopped at the output limit.",
            )
            return StructuredPayloadResult(None, metadata, issue)
        if isinstance(parsed, BaseModel):
            restored = restore_model(parsed, output_type, context)
            ensure_no_residual_placeholder(restored, self._pii_guard)
            return StructuredPayloadResult(restored.model_dump(), metadata)
        return decode_and_restore_payload(raw, metadata, context)


async def _invoke_model(structured_model: StructuredModel, system_prompt: str, protected_prompt: str) -> BaseModel:
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


async def _invoke_raw_model(
    structured_model: StructuredModel,
    system_prompt: str,
    protected_prompt: str,
) -> dict[str, object]:
    try:
        result = await structured_model.ainvoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=protected_prompt)]
        )
    except InfrastructureException:
        raise
    except Exception as exc:  # Provider SDK không có exception base chung.
        decision = LlmFailureClassifier().classify(exc)
        raise translate_llm_failure(decision) from exc
    if isinstance(result, dict):
        return result
    issue = "Native include_raw response has an invalid shape."
    return {"raw": None, "parsed": None, "parsing_error": issue}
