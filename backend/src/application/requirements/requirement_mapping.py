"""Pure mappings owned by the Requirement application module."""

from src.application.requirements.input import RequirementContext
from src.application.requirements.output import GeneratedRequirement
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.requirement.entities import Requirement
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.domain.requirement.value_objects import RequirementDetails
from src.domain.shared.types import EntityID


def to_requirement_context(requirement: Requirement) -> RequirementContext:
    """Expose only fields consumed by RequirementAgent."""
    return RequirementContext(
        requirement.id,
        requirement.title,
        requirement.description,
        requirement.type,
        requirement.priority,
    )


def map_generated_requirements(
    project_id: EntityID,
    items: tuple[GeneratedRequirement, ...],
    current: tuple[Requirement, ...] = (),
) -> tuple[Requirement, ...]:
    """Reconcile Agent output và bảo toàn identity/timestamp hợp lệ."""
    existing = {item.id: item for item in current}
    try:
        return tuple(
            _reconcile_requirement(project_id, item, existing)
            for item in items
        )
    except ValueError as exc:
        raise BusinessException(
            ErrorCode.INVALID_REQUIREMENT,
            "RequirementAgent returned an invalid requirement enum.",
        ) from exc


def _reconcile_requirement(
    project_id: EntityID,
    generated: GeneratedRequirement,
    existing: dict[EntityID, Requirement],
) -> Requirement:
    details = _generated_details(generated)
    current = existing.get(generated.existing_requirement_id)
    if generated.existing_requirement_id is not None and current is None:
        raise BusinessException(
            ErrorCode.INVALID_REQUIREMENT,
            "RequirementAgent tham chiếu Requirement ID không hiện hành.",
        )
    if current is None:
        return _new_requirement(project_id, details)
    if _current_details(current) != details:
        current.update(details)
    return current


def _generated_details(generated: GeneratedRequirement) -> RequirementDetails:
    return RequirementDetails(
        generated.title,
        generated.description,
        RequirementType(generated.requirement_type.upper()),
        RequirementPriority(generated.priority.upper()),
    )


def _current_details(current: Requirement) -> RequirementDetails:
    return RequirementDetails(
        current.title, current.description, current.type, current.priority
    )


def _new_requirement(
    project_id: EntityID, details: RequirementDetails
) -> Requirement:
    return Requirement(
        project_id=project_id,
        title=details.title,
        description=details.description,
        type=details.type,
        priority=details.priority,
    )
