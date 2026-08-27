"""Validate identity và map RequirementAgent structured output."""

from uuid import UUID

from src.application.requirements.output import (
    AnalyticalDerivationOutcome,
    AnalyticalDerivationStatus,
    GeneratedAnalyticalRequirement,
    GeneratedRequirement,
)
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.infrastructure.agents.transport_references import TransportReferenceMap
from src.infrastructure.llm.agent_structured_outputs import (
    AnalyticalDerivationOutcome as AnalyticalDerivationLlmOutcome,
)
from src.infrastructure.llm.agent_structured_outputs import (
    AnalyticalRequirementItem,
    GeneratedRequirementItem,
)


def map_requirement_items(
    items: list[GeneratedRequirementItem],
    references: TransportReferenceMap,
) -> tuple[GeneratedRequirement, ...]:
    """Từ chối foreign/duplicate ref trước khi map canonical candidates."""
    allowed = set(references.references)
    returned = [item.existing_requirement_ref for item in items if item.existing_requirement_ref]
    if len(returned) != len(set(returned)) or not set(returned).issubset(allowed):
        raise InfrastructureException(
            ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR,
            "RequirementAgent trả existing_requirement_ref lạ hoặc trùng.",
        )
    return tuple(_map_requirement(item, references) for item in items)


def map_derivation_outcome(
    item: AnalyticalDerivationLlmOutcome,
    requirement_id: UUID,
) -> AnalyticalDerivationOutcome:
    """Ánh xạ per-Requirement outcome và optional source-gap payload."""
    return AnalyticalDerivationOutcome(
        source_requirement_id=requirement_id,
        status=AnalyticalDerivationStatus(item.status),
        analytical_requirements=tuple(
            _map_analytical(requirement, requirement_id) for requirement in item.analytical_requirements
        ),
        reason=item.reason,
    )


def _map_requirement(
    item: GeneratedRequirementItem,
    references: TransportReferenceMap,
) -> GeneratedRequirement:
    return GeneratedRequirement(
        item.title,
        item.description,
        RequirementType(item.requirement_type),
        RequirementPriority(item.priority),
        references.resolve(item.existing_requirement_ref) if item.existing_requirement_ref else None,
    )


def _map_analytical(
    item: AnalyticalRequirementItem,
    requirement_id: UUID,
) -> GeneratedAnalyticalRequirement:
    return GeneratedAnalyticalRequirement(
        requirement_id,
        item.metric,
        item.dimension,
        item.time_granularity,
        item.aggregation_method,
        item.grain,
    )
