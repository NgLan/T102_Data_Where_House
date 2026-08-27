"""PII restoration và decoded payload validation cho structured LLM output."""

from dataclasses import dataclass
from typing import TypeVar

from pydantic import BaseModel
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.utils.json import safe_json_dumps
from src.infrastructure.llm.structured_output_decoder import decode_structured_payload
from src.infrastructure.llm.structured_output_models import (
    StructuredInvocationMetadata,
    StructuredOutputFailureCategory,
    StructuredOutputIssue,
    StructuredPayloadResult,
)
from src.infrastructure.llm.structured_raw_response import extract_raw_text
from src.infrastructure.security.pii_guard import PiiGuard

StructuredOutput = TypeVar("StructuredOutput", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class RestoreContext:
    """Context hoàn nguyên PII cho structured output."""

    mapping: dict[str, str]
    pii_guard: PiiGuard


def decode_and_restore_payload(
    raw: object,
    metadata: StructuredInvocationMetadata,
    context: RestoreContext,
) -> StructuredPayloadResult:
    """Decode raw JSON, hoàn nguyên PII và fail closed nếu placeholder hỏng."""
    raw_text = extract_raw_text(raw)
    if raw_text is None:
        issue = StructuredOutputIssue(
            StructuredOutputFailureCategory.JSON_NORMALIZATION_FAILED,
            "Raw structured response does not contain exactly one JSON payload.",
        )
        return StructuredPayloadResult(None, metadata, issue)
    payload, issue = decode_structured_payload(raw_text, metadata.finish_reason)
    if payload is None:
        return StructuredPayloadResult(None, metadata, issue)
    restored = _restore_value(payload, context)
    if not isinstance(restored, dict):
        return _invalid_root(metadata)
    _ensure_restored_value(restored, context.pii_guard)
    return StructuredPayloadResult(restored, metadata)


def ensure_no_residual_placeholder(result: BaseModel, pii_guard: PiiGuard) -> None:
    """Fail closed nếu typed output còn mã PII bị biến dạng."""
    _ensure_restored_value(result.model_dump(), pii_guard)


def restore_model(
    result: BaseModel,
    output_type: type[StructuredOutput],
    context: RestoreContext,
) -> StructuredOutput:
    """Hoàn nguyên mọi string field trong Pydantic output."""
    payload = _restore_value(result.model_dump(), context)
    return output_type.model_validate(payload)


def _restore_value(value: object, context: RestoreContext) -> object:
    if isinstance(value, str):
        return context.pii_guard.unmask(value, context.mapping)
    if isinstance(value, list):
        return [_restore_value(item, context) for item in value]
    if isinstance(value, dict):
        return {key: _restore_value(item, context) for key, item in value.items()}
    return value


def _ensure_restored_value(value: object, pii_guard: PiiGuard) -> None:
    if pii_guard.has_residual_placeholder(safe_json_dumps(value)):
        raise InfrastructureException(
            ErrorCode.LLM_PII_DEGRADATION_ERROR,
            "Mô hình ngôn ngữ làm biến dạng mã ẩn danh PII.",
        )


def _invalid_root(metadata: StructuredInvocationMetadata) -> StructuredPayloadResult:
    issue = StructuredOutputIssue(
        StructuredOutputFailureCategory.JSON_PARSE_ERROR,
        "Structured payload root must be an object.",
    )
    return StructuredPayloadResult(None, metadata, issue)
