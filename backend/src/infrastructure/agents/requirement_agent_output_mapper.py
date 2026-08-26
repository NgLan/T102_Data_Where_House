"""Validate identity và map RequirementAgent structured output."""

from uuid import UUID

from src.application.requirements.input import ClarifyRequirementsInput
from src.application.requirements.output import (
    AnalyticalDerivationOutcome,
    AnalyticalDerivationStatus,
    GeneratedAnalyticalRequirement,
    GeneratedRequirement,
)
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.infrastructure.llm.agent_structured_outputs import (
    AnalyticalDerivationOutcome as AnalyticalDerivationLlmOutcome,
)
from src.infrastructure.llm.agent_structured_outputs import (
    AnalyticalRequirementItem,
    GeneratedRequirementItem,
)


def map_requirement_items(
    items: list[GeneratedRequirementItem], data: ClarifyRequirementsInput
) -> tuple[GeneratedRequirement, ...]:
    """Từ chối foreign/duplicate ID trước khi map canonical candidates."""
    allowed = {str(item.id) for item in data.current_requirements}
    returned = [item.existing_requirement_id for item in items if item.existing_requirement_id]
    if len(returned) != len(set(returned)) or not set(returned).issubset(allowed):
        raise InfrastructureException(
            ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR,
            "RequirementAgent trả existing_requirement_id lạ hoặc trùng.",
        )
    return tuple(_map_requirement(item) for item in items)


def map_derivation_outcome(
    item: AnalyticalDerivationLlmOutcome,
) -> AnalyticalDerivationOutcome:
    """Ánh xạ per-Requirement outcome và optional source-gap payload."""
    return AnalyticalDerivationOutcome(
        source_requirement_id=UUID(item.source_requirement_id),
        status=AnalyticalDerivationStatus(item.status),
        analytical_requirements=tuple(
            _map_analytical(requirement) for requirement in item.analytical_requirements
        ),
        reason=item.reason,
    )


def _map_requirement(item: GeneratedRequirementItem) -> GeneratedRequirement:
    return GeneratedRequirement(
        item.title,
        item.description,
        RequirementType(item.requirement_type),
        RequirementPriority(item.priority),
        UUID(item.existing_requirement_id) if item.existing_requirement_id else None,
    )


def _map_analytical(item: AnalyticalRequirementItem) -> GeneratedAnalyticalRequirement:
    return GeneratedAnalyticalRequirement(
        UUID(item.source_requirement_id),
        item.metric,
        item.dimension,
        item.time_granularity,
        item.aggregation_method,
        item.grain,
    )
