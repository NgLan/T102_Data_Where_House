"""Public compatibility exports cho Agent structured-output schemas."""

from src.infrastructure.llm.analytical_structured_outputs import (
    AnalyticalDerivationOutcome,
    AnalyticalRequirementItem,
    AnalyticalRequirementResult,
)
from src.infrastructure.llm.dw_structured_outputs import (
    DbmlRevisionResult,
    DwConversationResult,
)
from src.infrastructure.llm.requirement_structured_outputs import (
    GeneratedRequirementItem,
    RequirementClarificationResult,
)
from src.infrastructure.llm.source_coverage_structured_outputs import (
    SourceCoverageLlmResult,
)
from src.infrastructure.llm.structured_output_base import AgentOutputBase

__all__ = [
    "AgentOutputBase",
    "AnalyticalDerivationOutcome",
    "AnalyticalRequirementItem",
    "AnalyticalRequirementResult",
    "DbmlRevisionResult",
    "DwConversationResult",
    "GeneratedRequirementItem",
    "RequirementClarificationResult",
    "SourceCoverageLlmResult",
]
