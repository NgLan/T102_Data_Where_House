"""Các thực thể thuộc miền Dự án (Project Entities)."""

from dataclasses import dataclass, field
from datetime import datetime

from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.datetime import ensure_utc, utc_now
from src.domain.project.enums import ProjectRole, ProjectStatus
from src.domain.project.project_status_rules import validate_project_editable, validate_status_transition
from src.domain.project.value_objects import ProjectDetails
from src.domain.shared.entity import BaseEntity
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID


@dataclass(eq=False, kw_only=True)
class Project(BaseEntity):
    """Thực thể đại diện cho Dự án (Project)."""

    name: str
    user_id: EntityID
    requirement: str | None = None
    requirement_revision: int = 0
    source_revision: int = 0
    analyzed_requirement_revision: int = 0
    analyzed_source_revision: int = 0
    description: str | None = None
    domain: str | None = None
    status: ProjectStatus = ProjectStatus.ACTIVE

    def __post_init__(self) -> None:
        """Thực thi kiểm tra dữ liệu đầu vào của Dự án."""
        super().__post_init__()
        self.status = normalize_str_enum(
            self.status,
            ProjectStatus,
            ErrorCode.INVALID_PROJECT_STATUS_TRANSITION,
        )
        details = ProjectDetails(
            name=self.name,
            requirement=self.requirement,
            domain=self.domain,
            description=self.description,
        )
        self._apply_details(details)
        if self.requirement and self.requirement_revision == 0:
            self.requirement_revision = 1

    def update_status(self, new_status: ProjectStatus) -> None:
        """Chuyển trạng thái dự án và cập nhật timestamp.

        Args:
            new_status: Trạng thái đích.

        Raises:
            BusinessException: Khi transition không được phép.
        """
        normalized_status = normalize_str_enum(
            new_status,
            ProjectStatus,
            ErrorCode.INVALID_PROJECT_STATUS_TRANSITION,
        )
        validate_status_transition(self.status, normalized_status)
        self.status = normalized_status
        self.mark_updated()

    def update_info(self, details: ProjectDetails) -> None:
        """Cập nhật thông tin dự án khi trạng thái cho phép.

        Args:
            details: Thông tin dự án đã được chuẩn hóa.

        Raises:
            BusinessException: Khi dự án không còn được chỉnh sửa.
        """
        validate_project_editable(self.status)
        previous_requirement = self.requirement
        self._apply_details(details)
        if self.requirement != previous_requirement:
            self.increment_requirement_revision()
        self.mark_updated()

    def increment_requirement_revision(self) -> None:
        """Tăng revision khi Raw Requirement được User lưu thay đổi."""
        self.requirement_revision += 1
        self.mark_updated()

    def increment_source_revision(self) -> None:
        """Tăng revision khi nội dung Data Source dùng cho analysis thay đổi."""
        self.source_revision += 1
        self.mark_updated()

    def is_requirement_analysis_outdated(self) -> bool:
        """Kiểm tra Raw Requirement hiện tại đã được phân tích chưa."""
        return self.requirement_revision != self.analyzed_requirement_revision

    def is_source_analysis_outdated(self) -> bool:
        """Kiểm tra schema hiện tại đã được dùng tạo Analytical Requirements chưa."""
        return self.source_revision != self.analyzed_source_revision

    def mark_requirement_analysis_completed(self) -> None:
        """Ghi nhận RequirementAgent đã xử lý revision hiện tại."""
        self.analyzed_requirement_revision = self.requirement_revision
        self.mark_updated()

    def mark_source_analysis_completed(self) -> None:
        """Ghi nhận Analytical Requirements đã dùng source revision hiện tại."""
        self.analyzed_source_revision = self.source_revision
        self.mark_updated()

    def _apply_details(self, details: ProjectDetails) -> None:
        """Áp dụng value object đã được kiểm tra vào entity."""
        self.name = details.name
        self.requirement = details.requirement
        self.domain = details.domain
        self.description = details.description

    def create_owner_member(self) -> "ProjectMember":
        """Tạo membership OWNER cho người tạo dự án.

        Returns:
            Membership liên kết project ID và user ID hiện tại.
        """
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
        self.role = normalize_str_enum(self.role, ProjectRole, ErrorCode.VALIDATION_ERROR)
        self.joined_at = ensure_utc(self.joined_at)
