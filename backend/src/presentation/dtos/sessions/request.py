"""Request DTO cho API phiên Agent."""

from typing import Annotated
from uuid import UUID

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field
from src.application.project_sessions.input import CreateSessionInput, RenameSessionInput, SendSessionMessageInput

ProjectSessionIdPath = Annotated[UUID, Path(description="ID phiên Agent")]


class CreateProjectSessionRequest(BaseModel):
    """Payload tạo session do người dùng chủ động khởi tạo."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str | None = Field(default=None, max_length=255)

    def to_application(self, project_id: UUID) -> CreateSessionInput:
        return CreateSessionInput(project_id, self.title)


class SendSessionMessageRequest(BaseModel):
    """Payload gửi message vào một session đã tồn tại."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    content: str = Field(min_length=1, max_length=2_000)

    def to_application(self, session_id: UUID) -> SendSessionMessageInput:
        return SendSessionMessageInput(session_id, self.content)


class RenameProjectSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=255)

    def to_application(self, session_id: UUID) -> RenameSessionInput:
        return RenameSessionInput(session_id, self.title)
