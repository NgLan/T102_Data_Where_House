"""Thực thể Yêu cầu (Requirement Entity)."""

from dataclasses import dataclass

from src.common.exceptions.error_codes import ErrorCode
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.domain.requirement.rules import normalize_requirement_fields
from src.domain.requirement.value_objects import RequirementDetails
from src.domain.shared.entity import BaseEntity
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID


@dataclass(eq=False, kw_only=True)
class Requirement(BaseEntity):
    """Thực thể đại diện cho Yêu cầu (Requirement) trong hệ thống."""

    project_id: EntityID
    type: RequirementType = RequirementType.BUSINESS
    title: str = ""
    description: str = ""
    priority: RequirementPriority = RequirementPriority.MEDIUM

    def __post_init__(self) -> None:
        """Thực thi kiểm tra quy tắc nghiệp vụ cho Yêu cầu."""
        super().__post_init__()
        self.type = normalize_str_enum(self.type, RequirementType, ErrorCode.VALIDATION_ERROR)
        self.priority = normalize_str_enum(
            self.priority,
            RequirementPriority,
            ErrorCode.VALIDATION_ERROR,
        )
        self.title, self.description = normalize_requirement_fields(
            self.title,
            self.description,
        )

    def update(self, details: RequirementDetails) -> None:
        """Cập nhật nội dung, phân loại và độ ưu tiên của Requirement."""
        self.title = details.title
        self.description = details.description
        self.type = details.type
        self.priority = details.priority
        self.mark_updated()
