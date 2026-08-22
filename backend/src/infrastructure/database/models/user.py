"""Model CSDL đại diện cho Bảng Người dùng (users)."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.domain.user.entities import MAX_USERNAME_LENGTH
from src.domain.user.value_objects import MAX_EMAIL_LENGTH
from src.infrastructure.database.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.data_model_change import DataModelChangeModel
    from src.infrastructure.database.models.project import ProjectModel
    from src.infrastructure.database.models.project_member import ProjectMemberModel
    from src.infrastructure.database.models.project_session import ProjectSessionModel


class UserModel(Base):
    """SQLAlchemy 2.0 ORM Model cho bảng users."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(MAX_USERNAME_LENGTH), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(MAX_EMAIL_LENGTH), nullable=False, unique=True, index=True)

    # Relationships
    projects: Mapped[list["ProjectModel"]] = relationship(
        "ProjectModel", back_populates="user", cascade="all, delete-orphan"
    )
    project_memberships: Mapped[list["ProjectMemberModel"]] = relationship(
        "ProjectMemberModel", back_populates="user", cascade="all, delete-orphan"
    )
    project_sessions: Mapped[list["ProjectSessionModel"]] = relationship(
        "ProjectSessionModel", back_populates="user", cascade="all, delete-orphan"
    )
    data_model_changes: Mapped[list["DataModelChangeModel"]] = relationship(
        "DataModelChangeModel", back_populates="user"
    )
