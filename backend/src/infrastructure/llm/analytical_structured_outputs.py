"""Structured output của analytical derivation operation."""

from pydantic import Field, model_validator
from src.application.requirements.output.models import AnalyticalDerivationStatus
from src.domain.analytical_requirement.enums import AggregationMethod
from src.infrastructure.llm.structured_output_base import (
    MIN_REQUIREMENTS_COUNT,
    AgentOutputBase,
    GroundedText,
)


class AnalyticalRequirementItem(AgentOutputBase):
    """Một Analytical Requirement gắn chính xác Requirement nguồn."""

    source_requirement_id: str
    metric: GroundedText | None = None
    dimension: GroundedText | None = None
    time_granularity: GroundedText | None = None
    aggregation_method: AggregationMethod | None = None
    grain: GroundedText | None = None


class AnalyticalDerivationOutcome(AgentOutputBase):
    """Discriminated outcome của đúng một Structured Requirement."""

    source_requirement_id: str
    status: AnalyticalDerivationStatus
    analytical_requirements: list[AnalyticalRequirementItem] = Field(default_factory=list)
    reason: GroundedText | None = None

    @model_validator(mode="after")
    def validate_outcome(self) -> "AnalyticalDerivationOutcome":
        """Bắt buộc payload tương ứng với trạng thái derivation."""
        items = self.analytical_requirements
        if self.status == AnalyticalDerivationStatus.READY:
            self._validate_ready(items)
        else:
            if not (self.reason or "").strip():
                raise ValueError("Non-ready outcome requires a reason.")
            self.analytical_requirements = []
        return self

    def _validate_ready(self, items: list[AnalyticalRequirementItem]) -> None:
        if not items:
            raise ValueError("READY requires items.")
        if any(item.source_requirement_id != self.source_requirement_id for item in items):
            raise ValueError("Nested source_requirement_id must match its outcome.")
        self.reason = None


class AnalyticalRequirementResult(AgentOutputBase):
    """Kết quả đầy đủ theo từng Requirement."""

    outcomes: list[AnalyticalDerivationOutcome] = Field(min_length=MIN_REQUIREMENTS_COUNT)
