"""Input model cho các thao tác Requirement."""

from dataclasses import dataclass

from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.domain.shared.types import EntityID


@dataclass(frozen=True)
class CreateRequirementInput:
    """Dữ liệu đầu vào để tạo mới một yêu cầu nghiệp vụ thô."""

    project_id: EntityID
    title: str
    description: str
    type: RequirementType
    priority: RequirementPriority


@dataclass(frozen=True)
class ListRequirementsInput:
    """Dữ liệu đầu vào để liệt kê yêu cầu của một dự án."""

    project_id: EntityID
