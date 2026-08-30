"""Request DTO cho API phiên Agent."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.application.project_sessions.input import (
    AnswerClarificationInput,
    CreateSessionInput,
    RenameSessionInput,
    SendSessionMessageInput,
)
from src.domain.project_session.enums import SessionPurpose

ProjectSessionIdPath = Annotated[UUID, Path(description="ID phiên Agent")]


class CreateProjectSessionRequest(BaseModel):
    """Payload tạo session do người dùng chủ động khởi tạo."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str | None = Field(default=None, max_length=255)
    purpose: SessionPurpose = Field(description="Mục đích nghiệp vụ của session")

    def to_application(self, project_id: UUID) -> CreateSessionInput:
        return CreateSessionInput(project_id, self.purpose, self.title)


class SendSessionMessageRequest(BaseModel):
    """Payload gửi message vào một session đã tồn tại."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    content: str = Field(min_length=1, max_length=2_000)
    client_message_id: UUID | None = None
    locale: Literal["vi", "en"] = "vi"

    def to_application(self, session_id: UUID) -> SendSessionMessageInput:
        return SendSessionMessageInput(
            session_id, self.content, self.client_message_id, self.locale
        )


class RenameProjectSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=255)

    def to_application(self, session_id: UUID) -> RenameSessionInput:
        return RenameSessionInput(session_id, self.title)


class AnswerClarificationRequest(BaseModel):
    """Chọn option có sẵn hoặc nhập câu trả lời tùy chỉnh."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    answer_type: Literal["option", "custom"]
    option_index: int | None = Field(default=None, ge=0, le=3)
    custom_answer: str | None = Field(default=None, min_length=1, max_length=2_000)

    @model_validator(mode="after")
    def validate_answer_shape(self) -> "AnswerClarificationRequest":
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
        self, session_id: UUID, question_id: UUID
    ) -> AnswerClarificationInput:
        return AnswerClarificationInput(
            session_id, question_id, self.option_index, self.custom_answer
        )
