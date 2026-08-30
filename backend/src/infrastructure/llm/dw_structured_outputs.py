"""Structured outputs của Data Warehouse Agent operations."""

from typing import Annotated, Literal
from uuid import UUID

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

    kind: Literal["clarification", "no_change", "proposal", "tool_request"]
    question: str | None
    options: list[Annotated[str, Field(min_length=MIN_TEXT_LENGTH)]] = Field(
        min_length=0, max_length=MAX_CLARIFICATION_OPTIONS
    )
    allow_custom_answer: bool
    reason: str | None
    dbml: str | None
    summary: str = Field(min_length=MIN_TEXT_LENGTH)
    tool_name: (
        Literal[
            "generate_data_model_analysis_document",
            "generate_data_model_ddl",
            "get_sandbox_config",
            "test_sandbox_connection",
            "execute_sandbox_ddl",
        ]
        | None
    ) = None
    target_kind: Literal["CURRENT_MODEL", "PROPOSAL"] | None = None
    proposal_change_id: UUID | None = None
    db_type: Literal["POSTGRESQL", "BIGQUERY", "SNOWFLAKE", "MYSQL", "SQLITE", "SQLSERVER"] | None = None
    reset_schema: bool | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "DwConversationResult":
        """Bắt buộc đúng payload tương ứng với discriminator."""
        if self.kind == "clarification":
            self._normalize_clarification()
            return self
        if self.kind == "tool_request":
            self._normalize_tool_request()
            return self
        self.question = None
        self.options = []
        self.allow_custom_answer = False
        self.reason = None
        if self.kind == "proposal" and not (self.dbml or "").strip():
            raise ValueError("Proposal result requires dbml.")
        if self.kind == "no_change" and self.dbml is not None:
            raise ValueError("No-change result cannot contain dbml.")
        self._clear_tool_request()
        return self

    def _normalize_tool_request(self) -> None:
        if self.tool_name is None or self.target_kind is None:
            raise ValueError("Tool request requires tool_name and target_kind.")
        self.question, self.reason, self.dbml = None, None, None
        self.options, self.allow_custom_answer = [], False
        self.db_type = self.db_type or "POSTGRESQL"

    def _clear_tool_request(self) -> None:
        self.tool_name, self.target_kind = None, None
        self.proposal_change_id, self.db_type, self.reset_schema = None, None, None

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
        self._clear_tool_request()
