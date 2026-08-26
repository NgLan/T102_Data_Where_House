"""ORM model cho Requirement Documents."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.base import Base
from src.infrastructure.database.constants import MAX_TITLE_LENGTH

if TYPE_CHECKING:
    from src.infrastructure.database.models.project import ProjectModel


class RequirementFileModel(Base):
    """Bảng metadata và extracted text của Requirement Document."""

    __tablename__ = "requirement_files"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(MAX_TITLE_LENGTH), nullable=False)
    file_type: Mapped[str] = mapped_column(String(16), nullable=False)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index("idx_requirement_files_project", "project_id"),
        Index(
            "uq_requirement_files_project_name_ci",
            "project_id",
            func.lower(name),
            unique=True,
        ),
    )

    project: Mapped["ProjectModel"] = relationship(
        "ProjectModel", back_populates="requirement_files"
    )
