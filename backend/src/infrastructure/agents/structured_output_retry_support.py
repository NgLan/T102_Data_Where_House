"""Per-item envelope validation cho RequirementAgent retry coordinators."""

from dataclasses import dataclass
from typing import TypeVar

from pydantic import BaseModel, ValidationError
from src.infrastructure.agents.structured_output_pydantic_validation import (
    pydantic_issue,
    validate_raw_outcome_envelope,
)
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputFailureCategory as Category,
)
from src.infrastructure.llm.structured_output_models import StructuredOutputIssue

OutputItem = TypeVar("OutputItem", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class ValidatedOutcomeBatch:
    """Các item hợp lệ và issue còn lại của một attempt."""

    values: dict[str, BaseModel]
    issues: tuple[StructuredOutputIssue, ...]


@dataclass(frozen=True, slots=True)
class OutcomeValidationSpec:
    """Identity contract deterministic của một outcome batch."""

    reference_field: str
    expected: frozenset[str]
    categories: tuple[Category, Category, Category]


@dataclass(frozen=True, slots=True)
class _IdentityComparison:
    missing: set[str]
    duplicate: set[str]
    unexpected: set[str]


@dataclass(frozen=True, slots=True)
class _ItemValidationContext:
    grouped: dict[str, list[dict[str, object]]]
    item_type: type[BaseModel]
    spec: OutcomeValidationSpec
    comparison: _IdentityComparison


def validate_outcome_batch(
    payload: dict[str, object],
    item_type: type[OutputItem],
    spec: OutcomeValidationSpec,
) -> ValidatedOutcomeBatch:
    """Validate identity trước Pydantic item mà không positional fallback."""
    raw_items, envelope_issue = validate_raw_outcome_envelope(payload)
    if raw_items is None:
        issue = envelope_issue or StructuredOutputIssue(Category.PYDANTIC_SCHEMA_ERROR, "Outcome envelope is invalid.")
        return ValidatedOutcomeBatch({}, (issue,))
    grouped = _group_by_reference(raw_items, spec.reference_field)
    comparison = _compare_identity(grouped, spec.expected)
    issues = _identity_issues(comparison, spec.categories)
    malformed = _malformed_issues(raw_items, spec)
    issues.extend(malformed)
    global_unknown = comparison.unexpected or malformed
    if global_unknown and not comparison.missing and not comparison.duplicate:
        return ValidatedOutcomeBatch({}, issues)
    values, schema_issues = _validate_items(_ItemValidationContext(grouped, item_type, spec, comparison))
    issues.extend(schema_issues)
    return ValidatedOutcomeBatch(values, tuple(issues))


def _validate_items(
    context: _ItemValidationContext,
) -> tuple[dict[str, BaseModel], list[StructuredOutputIssue]]:
    values: dict[str, BaseModel] = {}
    issues: list[StructuredOutputIssue] = []
    valid_refs = context.spec.expected - context.comparison.missing - context.comparison.duplicate
    for reference in valid_refs:
        try:
            raw = context.grouped[reference][0]
            values[reference] = context.item_type.model_validate(raw)
        except ValidationError as exc:
            issues.append(pydantic_issue(exc, reference))
    return values, issues


def _group_by_reference(
    items: list[dict[str, object]],
    field: str,
) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for item in items:
        reference = item.get(field)
        if isinstance(reference, str):
            grouped.setdefault(reference, []).append(item)
    return grouped


def _compare_identity(
    grouped: dict[str, list[dict[str, object]]],
    expected: frozenset[str],
) -> _IdentityComparison:
    actual = set(grouped)
    duplicate = {key for key, values in grouped.items() if len(values) > 1} & expected
    return _IdentityComparison(set(expected - actual), duplicate, actual - expected)


def _identity_issues(
    comparison: _IdentityComparison,
    categories: tuple[Category, Category, Category],
) -> list[StructuredOutputIssue]:
    issues = [
        StructuredOutputIssue(categories[0], "Expected reference is missing.", ref)
        for ref in sorted(comparison.missing)
    ]
    issues += [
        StructuredOutputIssue(categories[1], "Reference is duplicated.", ref) for ref in sorted(comparison.duplicate)
    ]
    issues += [
        StructuredOutputIssue(categories[2], "Reference is not canonical.", ref)
        for ref in sorted(comparison.unexpected)
    ]
    return issues


def _malformed_issues(
    items: list[dict[str, object]],
    spec: OutcomeValidationSpec,
) -> list[StructuredOutputIssue]:
    values = [item.get(spec.reference_field) for item in items]
    malformed = [value for value in values if not isinstance(value, str)]
    return [
        StructuredOutputIssue(
            spec.categories[2],
            "Reference is malformed.",
            str(value) if value is not None else None,
            spec.reference_field,
        )
        for value in malformed
    ]
