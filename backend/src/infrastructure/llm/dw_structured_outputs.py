"""Structured outputs của Data Warehouse Agent operations."""

from typing import Annotated, Literal

from pydantic import Field, model_validator
from src.infrastructure.llm.structured_output_base import (
    MAX_CLARIFICATION_OPTIONS,
    MIN_CLARIFICATION_OPTIONS,
    MIN_TEXT_LENGTH,
    AgentOutputBase,
)


class DbmlRevisionResult(AgentOutputBase):
    """Toàn bộ DBML do một DWDesignAgent invocation sinh."""

    dbml: str = Field(min_length=MIN_TEXT_LENGTH)


class DwConversationResult(AgentOutputBase):
    """Kết quả quyết định của một lượt hội thoại chỉnh sửa Data Model."""

    kind: Literal["clarification", "no_change", "proposal"]
    question: str | None
    options: list[Annotated[str, Field(min_length=MIN_TEXT_LENGTH)]] = Field(
        min_length=0, max_length=MAX_CLARIFICATION_OPTIONS
    )
    allow_custom_answer: bool
    reason: str | None
    dbml: str | None
    summary: str = Field(min_length=MIN_TEXT_LENGTH)

    @model_validator(mode="after")
    def validate_payload(self) -> "DwConversationResult":
        """Bắt buộc đúng payload tương ứng với discriminator."""
        if self.kind == "clarification":
            self._normalize_clarification()
            return self
        self.question = None
        self.options = []
        self.allow_custom_answer = False
        self.reason = None
        if self.kind == "proposal" and not (self.dbml or "").strip():
            raise ValueError("Proposal result requires dbml.")
        if self.kind == "no_change" and self.dbml is not None:
            raise ValueError("No-change result cannot contain dbml.")
        return self

    def _normalize_clarification(self) -> None:
        normalized = [option.strip() for option in self.options if option.strip()]
        if len(set(normalized)) != len(normalized):
            raise ValueError("Clarification options must be unique.")
        valid_count = MIN_CLARIFICATION_OPTIONS <= len(normalized) <= MAX_CLARIFICATION_OPTIONS
        if not (self.question or "").strip() or not valid_count:
            raise ValueError("Clarification requires one question and 1-4 options.")
        if not (self.reason or "").strip():
            raise ValueError("Clarification requires a concrete reason.")
        self.options = normalized
        self.allow_custom_answer = True
        self.dbml = None
