"""Module quản lý Yêu cầu Phân tích (Analytical Requirement Domain)."""

from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import (
    AggregationMethod,
    SourceCandidateKind,
    SourceConfirmationQuestionType,
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
)
from src.domain.analytical_requirement.source_coverage_candidate import (
    SourceCoverageCandidate,
    SourceCoverageReference,
)

__all__: list[str] = [
    "AnalyticalRequirement",
    "AggregationMethod",
    "SourceCandidateKind",
    "SourceConfirmationQuestionType",
    "SourceConfirmationStatus",
    "SourceCoverageResolutionAction",
    "SourceCoverageAssessment",
    "SourceCoverageCandidate",
    "SourceCoverageReference",
    "SourceCoverageStatus",
    "IAnalyticalRequirementRepository",
    "validate_analytical_requirement",
]
