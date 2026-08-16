"""Các thực thể thuộc miền Dự án (Project Entities)."""

from dataclasses import dataclass, field
from datetime import datetime

from src.common.utils.datetime import ensure_utc, utc_now
from src.domain.project.enums import ProjectRole, ProjectStatus
from src.domain.project.rules import validate_project_editable, validate_status_transition
from src.domain.project.value_objects import ProjectDetails
from src.domain.shared.entity import BaseEntity
from src.domain.shared.types import EntityID


@dataclass(eq=False, kw_only=True)
class Project(BaseEntity):
    """Thực thể đại diện cho Dự án (Project)."""

    name: str
    requirement: str
    user_id: EntityID
    description: str | None = None
    domain: str | None = None
    status: ProjectStatus = ProjectStatus.ACTIVE

    def __post_init__(self) -> None:
        """Thực thi kiểm tra dữ liệu đầu vào của Dự án."""
        super().__post_init__()
        details = ProjectDetails(
            name=self.name,
            requirement=self.requirement,
            domain=self.domain,
            description=self.description,
        )
        self._apply_details(details)

    def update_status(self, new_status: ProjectStatus) -> None:
        """Cập nhật trạng thái mới cho dự án."""
        validate_status_transition(self.status, new_status)
        self.status = new_status
        self.mark_updated()

    def update_info(self, details: ProjectDetails) -> None:
        """Cập nhật thông tin dự án khi trạng thái cho phép."""
        validate_project_editable(self.status)
        self._apply_details(details)
        self.mark_updated()

    def _apply_details(self, details: ProjectDetails) -> None:
        """Áp dụng value object đã được kiểm tra vào entity."""
        self.name = details.name
        self.requirement = details.requirement
        self.domain = details.domain
        self.description = details.description

    def create_owner_member(self) -> "ProjectMember":
        """Tạo thực thể thành viên dự án với vai trò OWNER cho người tạo dự án."""
        return ProjectMember(
            project_id=self.id,
            user_id=self.user_id,
            role=ProjectRole.OWNER,
        )


@dataclass(eq=False, kw_only=True)
class ProjectMember(BaseEntity):
    """Thực thể đại diện cho Thành viên tham gia Dự án."""

    project_id: EntityID
    user_id: EntityID
    role: ProjectRole = ProjectRole.MEMBER
    joined_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        """Đảm bảo mốc thời gian joined_at có timezone UTC."""
        super().__post_init__()
        self.joined_at = ensure_utc(self.joined_at)
