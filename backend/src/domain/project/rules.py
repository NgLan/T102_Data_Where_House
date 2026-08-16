"""Quy tắc nghiệp vụ thuần cho miền Dự án."""

from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.string import normalize_whitespace, safe_strip
from src.domain.project.enums import ProjectStatus

MIN_PROJECT_NAME_LENGTH = 3
MAX_PROJECT_NAME_LENGTH = 255
MIN_PROJECT_REQUIREMENT_LENGTH = 10
MAX_PROJECT_DOMAIN_LENGTH = 100

_ALLOWED_STATUS_TRANSITIONS: dict[ProjectStatus, frozenset[ProjectStatus]] = {
    ProjectStatus.ACTIVE: frozenset({ProjectStatus.ANALYZING, ProjectStatus.ARCHIVED}),
    ProjectStatus.ANALYZING: frozenset({ProjectStatus.ACTIVE}),
    ProjectStatus.ARCHIVED: frozenset({ProjectStatus.ACTIVE}),
}


def normalize_project_name(name: str) -> str:
    """Chuẩn hóa và kiểm tra tên dự án."""
    normalized = normalize_whitespace(name)
    if len(normalized) < MIN_PROJECT_NAME_LENGTH:
        raise BusinessException(
            code=ErrorCode.INVALID_PROJECT_NAME,
            message=f"Tên dự án phải có ít nhất {MIN_PROJECT_NAME_LENGTH} ký tự.",
        )
    if len(normalized) > MAX_PROJECT_NAME_LENGTH:
        raise BusinessException(
            code=ErrorCode.PROJECT_NAME_TOO_LONG,
            message=f"Tên dự án không được vượt quá {MAX_PROJECT_NAME_LENGTH} ký tự.",
        )
    return normalized


def normalize_project_requirement(requirement: str) -> str:
    """Chuẩn hóa và kiểm tra yêu cầu nghiệp vụ của dự án."""
    normalized = normalize_whitespace(requirement)
    if len(normalized) < MIN_PROJECT_REQUIREMENT_LENGTH:
        raise BusinessException(
            code=ErrorCode.INVALID_PROJECT_REQUIREMENT,
            message=f"Yêu cầu nghiệp vụ phải có ít nhất {MIN_PROJECT_REQUIREMENT_LENGTH} ký tự.",
        )
    return normalized


def normalize_project_domain(domain: str | None) -> str | None:
    """Chuẩn hóa domain tùy chọn và bảo vệ giới hạn lưu trữ."""
    normalized = safe_strip(domain)
    if normalized == "":
        return None
    if normalized is not None and len(normalized) > MAX_PROJECT_DOMAIN_LENGTH:
        raise BusinessException(
            code=ErrorCode.INVALID_PROJECT_DOMAIN,
            message=f"Lĩnh vực nghiệp vụ không được vượt quá {MAX_PROJECT_DOMAIN_LENGTH} ký tự.",
        )
    return normalized


def validate_project_editable(status: ProjectStatus) -> None:
    """Bảo đảm dự án đang ở trạng thái cho phép chỉnh sửa."""
    if status != ProjectStatus.ACTIVE:
        raise BusinessException(
            code=ErrorCode.INVALID_PROJECT_STATUS_TRANSITION,
            message="Chỉ dự án đang hoạt động mới được phép chỉnh sửa.",
        )


def validate_status_transition(current: ProjectStatus, target: ProjectStatus) -> None:
    """Kiểm tra state transition của dự án."""
    if target not in _ALLOWED_STATUS_TRANSITIONS[current]:
        raise BusinessException(
            code=ErrorCode.INVALID_PROJECT_STATUS_TRANSITION,
            message=f"Không thể chuyển trạng thái dự án từ {current.value} sang {target.value}.",
        )
