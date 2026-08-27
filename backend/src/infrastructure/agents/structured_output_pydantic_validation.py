"""Root-envelope và Pydantic error normalization cho structured output."""

from pydantic import BaseModel, ConfigDict, ValidationError
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputFailureCategory as Category,
)
from src.infrastructure.llm.structured_output_models import StructuredOutputIssue


class RawOutcomeEnvelope(BaseModel):
    """Envelope chỉ validate root để item có thể được salvage độc lập."""

    model_config = ConfigDict(extra="forbid")
    outcomes: list[dict[str, object]]


def validate_raw_outcome_envelope(
    payload: dict[str, object],
) -> tuple[list[dict[str, object]] | None, StructuredOutputIssue | None]:
    """Validate root mà chưa validate aggregate item schema."""
    try:
        return RawOutcomeEnvelope.model_validate(payload).outcomes, None
    except ValidationError as exc:
        return None, pydantic_issue(exc, None)


def pydantic_issue(
    exc: ValidationError,
    reference: str | None,
) -> StructuredOutputIssue:
    """Chuyển Pydantic error đầu tiên thành feedback không chứa raw payload."""
    error = exc.errors(include_url=False)[0]
    field = ".".join(str(value) for value in error.get("loc", ())) or None
    message = str(error.get("msg", "Pydantic validation failed."))
    category = Category.SEMANTIC_FIELD_MISSING if "requires" in message.casefold() else Category.PYDANTIC_SCHEMA_ERROR
    return StructuredOutputIssue(category, message, reference, field, exc)
