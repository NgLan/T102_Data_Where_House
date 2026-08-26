"""Request DTO cho Requirement clarification commands."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.application.requirements.input import (
    AnalyzeRequirementClarificationInput,
    AnswerRequirementClarificationInput,
    ChooseRequirementContinuationInput,
    SendRequirementClarificationMessageInput,
)
from src.domain.project_session.enums import RequirementContinuationAction


class AnalyzeRequirementClarificationRequest(BaseModel):
    """Analyze revision đã lưu, không nhận draft editor."""

    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=0)

    def to_application(self, project_id: UUID) -> AnalyzeRequirementClarificationInput:
        return AnalyzeRequirementClarificationInput(project_id, self.expected_revision)


class AnswerRequirementClarificationRequest(BaseModel):
    """Chọn grounded option hoặc gửi custom answer."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    answer_type: Literal["option", "custom"]
    option_index: int | None = Field(default=None, ge=0, le=3)
    custom_answer: str | None = Field(default=None, min_length=1, max_length=2_000)

    @model_validator(mode="after")
    def validate_answer(self) -> "AnswerRequirementClarificationRequest":
        if self.answer_type == "option" and self.option_index is None:
            raise ValueError("option_index is required for an option answer.")
        if self.answer_type == "custom" and not self.custom_answer:
            raise ValueError("custom_answer is required for a custom answer.")
        if self.answer_type == "option" and self.custom_answer is not None:
            raise ValueError("custom_answer is not allowed for an option answer.")
        if self.answer_type == "custom" and self.option_index is not None:
            raise ValueError("option_index is not allowed for a custom answer.")
        return self

    def to_application(
        self, project_id: UUID, session_id: UUID, question_id: UUID
    ) -> AnswerRequirementClarificationInput:
        return AnswerRequirementClarificationInput(
            project_id,
            session_id,
            question_id,
            self.option_index,
            self.custom_answer,
        )


class SendRequirementClarificationMessageRequest(BaseModel):
    """Tin nhắn follow-up không phụ thuộc pending question."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    expected_revision: int = Field(ge=0)
    message: str = Field(min_length=1, max_length=2_000)

    def to_application(
        self, project_id: UUID, session_id: UUID
    ) -> SendRequirementClarificationMessageInput:
        return SendRequirementClarificationMessageInput(
            project_id, session_id, self.expected_revision, self.message
        )


class ChooseRequirementContinuationRequest(BaseModel):
    """Action tại continuation gate của current Requirement revision."""

    model_config = ConfigDict(extra="forbid")
    action: RequirementContinuationAction
    expected_revision: int = Field(ge=0)

    def to_application(
        self, project_id: UUID, session_id: UUID
    ) -> ChooseRequirementContinuationInput:
        return ChooseRequirementContinuationInput(
            project_id, session_id, self.action, self.expected_revision
        )
