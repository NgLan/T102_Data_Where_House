"""Typed diagnostics cho quá trình nhận structured output từ LLM."""

from dataclasses import dataclass
from dataclasses import field as dataclass_field
from enum import StrEnum


class StructuredOutputFailureCategory(StrEnum):
    """Phân loại nội bộ, không đi qua public API error code."""

    JSON_NORMALIZATION_FAILED = "JSON_NORMALIZATION_FAILED"
    JSON_PARSE_ERROR = "JSON_PARSE_ERROR"
    JSON_REPAIR_FAILED = "JSON_REPAIR_FAILED"
    OUTPUT_TRUNCATED = "OUTPUT_TRUNCATED"
    PYDANTIC_SCHEMA_ERROR = "PYDANTIC_SCHEMA_ERROR"
    REQUIREMENT_REF_MISSING = "REQUIREMENT_REF_MISSING"
    REQUIREMENT_REF_DUPLICATED = "REQUIREMENT_REF_DUPLICATED"
    REQUIREMENT_REF_UNKNOWN = "REQUIREMENT_REF_UNKNOWN"
    ANALYTICAL_REF_MISSING = "ANALYTICAL_REF_MISSING"
    ANALYTICAL_REF_DUPLICATED = "ANALYTICAL_REF_DUPLICATED"
    ANALYTICAL_REF_UNKNOWN = "ANALYTICAL_REF_UNKNOWN"
    SOURCE_REF_UNKNOWN = "SOURCE_REF_UNKNOWN"
    SOURCE_TABLE_UNKNOWN = "SOURCE_TABLE_UNKNOWN"
    SOURCE_COLUMN_UNKNOWN = "SOURCE_COLUMN_UNKNOWN"
    SOURCE_RELATIONSHIP_UNKNOWN = "SOURCE_RELATIONSHIP_UNKNOWN"
    SEMANTIC_FIELD_MISSING = "SEMANTIC_FIELD_MISSING"


@dataclass(frozen=True, slots=True)
class StructuredOutputIssue:
    """Một lỗi validation an toàn để log và đưa vào retry prompt."""

    category: StructuredOutputFailureCategory
    message: str
    reference: str | None = None
    field: str | None = None
    cause: Exception | None = dataclass_field(default=None, compare=False, repr=False)


@dataclass(frozen=True, slots=True)
class StructuredInvocationMetadata:
    """Metadata provider không chứa prompt hoặc raw response."""

    finish_reason: str | None = None
    provider: str | None = None
    model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True, slots=True)
class StructuredPayloadResult:
    """Payload JSON đã phục hồi hoặc issue khiến caller quyết định retry."""

    payload: dict[str, object] | None
    metadata: StructuredInvocationMetadata
    issue: StructuredOutputIssue | None = None


class StructuredOutputItemError(ValueError):
    """Báo một item sai contract mà chưa dịch sang public exception."""

    def __init__(self, issue: StructuredOutputIssue) -> None:
        super().__init__(issue.message)
        self.issue = issue
