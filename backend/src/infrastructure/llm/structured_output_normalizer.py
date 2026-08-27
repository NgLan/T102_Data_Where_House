"""Conservative extraction of one JSON candidate from provider text."""

import json
import re

from src.infrastructure.llm.structured_output_models import (
    StructuredOutputFailureCategory as Category,
)
from src.infrastructure.llm.structured_output_models import StructuredOutputIssue

_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)


def normalize_structured_text(
    raw_text: str,
) -> tuple[str, StructuredOutputIssue | None]:
    """Bỏ wrapper hình thức chỉ khi có đúng một JSON candidate."""
    value = raw_text.lstrip("\ufeff").strip()
    if not value:
        return "", _issue("Structured response is empty.")
    fenced = list(_FENCE.finditer(value))
    if len(fenced) > 1:
        return "", _issue("Multiple JSON candidates found.")
    if fenced:
        return _normalize_fence(value, fenced[0])
    candidates = _json_candidates(value)
    if len(candidates) > 1:
        return "", _issue("Multiple JSON candidates found.")
    if not candidates and value[:1] not in "{[":
        return "", _issue("No unambiguous JSON payload found.")
    return candidates[0] if candidates else value, None


def _normalize_fence(
    value: str,
    fenced: re.Match[str],
) -> tuple[str, StructuredOutputIssue | None]:
    outside = value[: fenced.start()] + value[fenced.end() :]
    candidate = fenced.group(1).strip()
    if _json_candidates(outside) or len(_json_candidates(candidate)) > 1:
        return "", _issue("Multiple JSON candidates found.")
    return candidate, None


def _json_candidates(value: str) -> list[str]:
    decoder = json.JSONDecoder()
    candidates: list[str] = []
    cursor = 0
    while cursor < len(value):
        positions = _candidate_positions(value, cursor)
        if not positions:
            break
        index = min(positions)
        try:
            parsed, end = decoder.raw_decode(value[index:])
        except json.JSONDecodeError:
            if index == 0:
                return []
            cursor = index + 1
            continue
        if isinstance(parsed, (dict, list)):
            candidates.append(value[index : index + end])
            cursor = index + end
    return candidates


def _candidate_positions(value: str, cursor: int) -> list[int]:
    return [index for index in (value.find("{", cursor), value.find("[", cursor)) if index >= 0]


def _issue(message: str) -> StructuredOutputIssue:
    return StructuredOutputIssue(Category.JSON_NORMALIZATION_FAILED, message)
