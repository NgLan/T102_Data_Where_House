"""Normalize và repair JSON hình thức mà không suy diễn semantic."""

import json
import re

from json_repair import repair_json
from src.common.utils.json import safe_json_loads
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputFailureCategory as Category,
)
from src.infrastructure.llm.structured_output_models import StructuredOutputIssue
from src.infrastructure.llm.structured_output_normalizer import normalize_structured_text

_MISSING_VALUE = re.compile(r":\s*(?=[,}\]])")


def decode_structured_payload(
    raw_text: str,
    finish_reason: str | None,
) -> tuple[dict[str, object] | None, StructuredOutputIssue | None]:
    """Trả JSON object khi có thể phục hồi cú pháp một cách bảo thủ."""
    if is_truncated_finish(finish_reason):
        return None, _issue(Category.OUTPUT_TRUNCATED, "Provider stopped at the output limit.")
    normalized, issue = normalize_structured_text(raw_text)
    if issue:
        return None, issue
    try:
        parsed = safe_json_loads(normalized)
    except ValueError:
        unsafe = _unsafe_repair_reason(normalized)
        if unsafe:
            return None, _issue(Category.OUTPUT_TRUNCATED, unsafe)
        if not _is_allowed_syntax_error(normalized):
            return None, _issue(Category.JSON_PARSE_ERROR, "JSON syntax is not repair-eligible.")
        return _repair(normalized)
    return _require_object(parsed, Category.JSON_PARSE_ERROR)


def _is_allowed_syntax_error(value: str) -> bool:
    try:
        json.loads(value)
    except json.JSONDecodeError as cause:
        return _is_allowlisted_decode_error(cause, value)
    return False


def _is_allowlisted_decode_error(cause: json.JSONDecodeError, value: str) -> bool:
    if cause.msg.startswith("Illegal trailing comma before end of"):
        return True
    allowed = (
        "Expecting property name enclosed in double quotes",
        "Expecting ',' delimiter",
        "Expecting ':' delimiter",
        "Invalid \\escape",
    )
    if cause.msg in allowed:
        return True
    trailing_comma = re.match(r",\s*[\]}]", value[cause.pos :]) is not None
    preceding_comma = value[: cause.pos].rstrip().endswith(",")
    return cause.msg == "Expecting value" and (trailing_comma or preceding_comma)


def _repair(value: str) -> tuple[dict[str, object] | None, StructuredOutputIssue | None]:
    unsafe = _unsafe_repair_reason(value)
    if unsafe:
        return None, _issue(Category.OUTPUT_TRUNCATED, unsafe)
    try:
        repaired = repair_json(
            value,
            return_objects=True,
            skip_json_loads=True,
            ensure_ascii=False,
        )
    except (ValueError, TypeError, RecursionError):
        return None, _issue(Category.JSON_REPAIR_FAILED, "JSON syntax repair failed.")
    return _require_object(repaired, Category.JSON_REPAIR_FAILED)


def _unsafe_repair_reason(value: str) -> str | None:
    if _MISSING_VALUE.search(value) or value.rstrip().endswith(":"):
        return "JSON contains a key without a semantic value."
    depth, in_string, escaped = 0, False, False
    for char in value:
        if char == '"' and not escaped:
            in_string = not in_string
        if not in_string and char in "{[":
            depth += 1
        elif not in_string and char in "}]":
            depth -= 1
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
    if in_string or depth != 0:
        return "JSON is truncated or has an unterminated value."
    return None


def _require_object(
    value: object,
    category: Category,
) -> tuple[dict[str, object] | None, StructuredOutputIssue | None]:
    if isinstance(value, dict):
        return value, None
    return None, _issue(category, "Structured payload root must be a JSON object.")


def is_truncated_finish(reason: str | None) -> bool:
    """Nhận diện các finish reason cho biết provider đã cắt output."""
    return (reason or "").casefold() in {"length", "max_tokens", "max tokens"}


def _issue(category: Category, message: str) -> StructuredOutputIssue:
    return StructuredOutputIssue(category, message)
