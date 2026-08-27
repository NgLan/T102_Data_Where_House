"""Structured output của Requirement clarification operation."""

from typing import Annotated, Literal

from pydantic import Field, model_validator
from src.domain.project_session.enums import RequirementClarificationStatus
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.infrastructure.llm.structured_output_base import (
    MAX_CLARIFICATION_OPTIONS,
    MIN_CLARIFICATION_OPTIONS,
    MIN_REQUIREMENTS_COUNT,
    MIN_TEXT_LENGTH,
    AgentOutputBase,
)


class GeneratedRequirementItem(AgentOutputBase):
    """Một Requirement có cấu trúc do RequirementAgent sinh."""

    title: str = Field(min_length=MIN_TEXT_LENGTH)
    description: str = Field(min_length=MIN_TEXT_LENGTH)
    requirement_type: RequirementType
    priority: RequirementPriority = RequirementPriority.MEDIUM
    existing_requirement_ref: str | None = Field(
        description="Required exact current R-reference, or null for a new item."
    )


class RequirementClarificationResult(AgentOutputBase):
    """Kết quả cấu trúc hóa kèm readiness và câu hỏi tập trung."""

    requirements: list[GeneratedRequirementItem] = Field(
        min_length=MIN_REQUIREMENTS_COUNT
    )
    status: Literal[
        RequirementClarificationStatus.NEEDS_CLARIFICATION,
        RequirementClarificationStatus.READY,
    ]
    question: str | None = None
    options: list[Annotated[str, Field(min_length=MIN_TEXT_LENGTH)]] = Field(
        default_factory=list, max_length=MAX_CLARIFICATION_OPTIONS
    )
    allow_custom_answer: bool = False
    reason: str | None = None
    summary: str = ""

    @model_validator(mode="after")
    def validate_clarification(self) -> "RequirementClarificationResult":
        """Bảo đảm discriminator và payload luôn đồng bộ."""
        if self.status == RequirementClarificationStatus.NEEDS_CLARIFICATION:
            self._validate_pending()
        else:
            self.question = None
            self.options = []
            self.allow_custom_answer = False
            self.reason = None
        return self

    def _validate_pending(self) -> None:
        normalized = [item.strip() for item in self.options if item.strip()]
        if len(set(normalized)) != len(normalized):
            raise ValueError("Clarification options must be unique.")
        valid_count = MIN_CLARIFICATION_OPTIONS <= len(normalized) <= MAX_CLARIFICATION_OPTIONS
        if not (self.question or "").strip() or not valid_count:
            raise ValueError("Clarification requires one question and 1-4 options.")
        if not (self.reason or "").strip():
            raise ValueError("Clarification requires a concrete reason.")
        self.options = normalized
        self.allow_custom_answer = True
