"""Project membership entity."""

from dataclasses import dataclass, field
from datetime import datetime

from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.datetime import ensure_utc, utc_now
from src.domain.project.enums import ProjectRole
from src.domain.shared.entity import BaseEntity
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID


@dataclass(eq=False, kw_only=True)
class ProjectMember(BaseEntity):
    """Thành viên và role trong một Project."""

    project_id: EntityID
    user_id: EntityID
    role: ProjectRole = ProjectRole.MEMBER
    joined_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        """Chuẩn hóa role và thời điểm tham gia về UTC."""
        super().__post_init__()
        self.role = normalize_str_enum(
            self.role, ProjectRole, ErrorCode.VALIDATION_ERROR
        )
        self.joined_at = ensure_utc(self.joined_at)
