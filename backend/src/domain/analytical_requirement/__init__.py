"""Module quản lý Yêu cầu Phân tích (Analytical Requirement Domain)."""

from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import (
    AggregationMethod,
    SourceCandidateKind,
    SourceConfirmationStatus,
    SourceCoverageResolutionAction,
    SourceCoverageStatus,
)
from src.domain.analytical_requirement.i_analytical_requirement_repository import (
    IAnalyticalRequirementRepository,
)
from src.domain.analytical_requirement.rules import validate_analytical_requirement
from src.domain.analytical_requirement.source_coverage import (
    SourceCoverageAssessment,
    SourceCoverageCandidate,
)

__all__: list[str] = [
    "AnalyticalRequirement",
    "AggregationMethod",
    "SourceCandidateKind",
    "SourceConfirmationStatus",
    "SourceCoverageResolutionAction",
    "SourceCoverageAssessment",
    "SourceCoverageCandidate",
    "SourceCoverageStatus",
    "IAnalyticalRequirementRepository",
    "validate_analytical_requirement",
]
