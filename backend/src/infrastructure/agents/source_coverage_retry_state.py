"""Mutable in-memory state cho một bounded Source Coverage retry sequence."""

from dataclasses import dataclass

from src.application.requirements.input import EvaluateSourceCoverageInput
from src.application.requirements.output import SourceCoverageOutcome
from src.infrastructure.agents.source_coverage_output_mapper import (
    SourceCoverageMappingContext,
)
from src.infrastructure.agents.transport_references import SourceCoverageReferenceBoundary
from src.infrastructure.llm.structured_output_models import StructuredOutputIssue


@dataclass(slots=True)
class SourceCoverageRetryState:
    """Accepted outcomes chỉ tồn tại trong memory đến khi coverage đầy đủ."""

    data: EvaluateSourceCoverageInput
    references: SourceCoverageReferenceBoundary
    mapping: SourceCoverageMappingContext
    pending: set[str]
    accepted: dict[str, SourceCoverageOutcome]
    issues: tuple[StructuredOutputIssue, ...] = ()
    last_issue: StructuredOutputIssue | None = None
