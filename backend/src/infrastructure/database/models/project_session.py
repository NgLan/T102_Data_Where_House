"""Model CSDL đại diện cho Bảng Phiên Agent (project_sessions)."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.domain.shared.types import JsonValue
from src.infrastructure.database.base import Base
from src.infrastructure.database.constants import MAX_STATUS_LENGTH, MAX_TITLE_LENGTH

if TYPE_CHECKING:
    from src.infrastructure.database.models.project import ProjectModel
    from src.infrastructure.database.models.session_event import SessionEventModel
    from src.infrastructure.database.models.user import UserModel


class ProjectSessionModel(Base):
    """SQLAlchemy 2.0 ORM Model cho bảng project_sessions."""

    __tablename__ = "project_sessions"

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(MAX_TITLE_LENGTH), nullable=True)
    status: Mapped[str] = mapped_column(String(MAX_STATUS_LENGTH), nullable=False, default="ACTIVE", index=True)
    purpose: Mapped[str] = mapped_column(String(MAX_STATUS_LENGTH), nullable=False, default="DATA_MODELING")
    base_requirement_revision: Mapped[int | None] = mapped_column(nullable=True)
    requirement_continuation_state: Mapped[str] = mapped_column(
        String(MAX_STATUS_LENGTH), nullable=False, default="NOT_REQUIRED"
    )
    active_turn_id: Mapped[UUID | None] = mapped_column(nullable=True)
    active_turn_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pending_question_id: Mapped[UUID | None] = mapped_column(nullable=True, index=True)
    conversation_summary: Mapped[dict[str, JsonValue] | None] = mapped_column(JSONB, nullable=True)
    summarized_through_event_id: Mapped[UUID | None] = mapped_column(nullable=True)
    summary_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_project_sessions_project_status", "project_id", "status"),
        Index("idx_project_sessions_project_purpose_status", "project_id", "purpose", "status"),
        Index(
            "uq_project_active_requirement_session",
            "project_id",
            unique=True,
            postgresql_where=text(
                "purpose = 'REQUIREMENT_CLARIFICATION' AND status = 'ACTIVE'"
            ),
            sqlite_where=text(
                "purpose = 'REQUIREMENT_CLARIFICATION' AND status = 'ACTIVE'"
            ),
        ),
    )

    # Relationships
    project: Mapped["ProjectModel"] = relationship("ProjectModel", back_populates="sessions")
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="project_sessions")
    events: Mapped[list["SessionEventModel"]] = relationship(
        "SessionEventModel", back_populates="session", cascade="all, delete-orphan"
    )
