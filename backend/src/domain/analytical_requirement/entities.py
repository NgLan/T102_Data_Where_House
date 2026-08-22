"""Thực thể Yêu cầu Phân tích (Analytical Requirement Entity)."""

from dataclasses import dataclass

from src.common.exceptions.error_codes import ErrorCode
from src.domain.analytical_requirement.enums import AggregationMethod
from src.domain.analytical_requirement.rules import validate_analytical_requirement
from src.domain.shared.entity import BaseEntity
from src.domain.shared.enum_rules import normalize_str_enum
from src.domain.shared.types import EntityID


@dataclass(eq=False, kw_only=True)
class AnalyticalRequirement(BaseEntity):
    """Thực thể đại diện cho Yêu cầu Phân tích chi tiết (Analytical Requirement)."""

    requirement_id: EntityID
    metric: str | None = None
    dimension: str | None = None
    time_granularity: str | None = None
    aggregation_method: AggregationMethod | None = None
    grain: str | None = None

    def __post_init__(self) -> None:
        """Thực thi kiểm tra quy tắc nghiệp vụ cho Yêu cầu Phân tích."""
        super().__post_init__()

        if isinstance(self.aggregation_method, str):
            self.aggregation_method = normalize_str_enum(
                self.aggregation_method,
                AggregationMethod,
                ErrorCode.VALIDATION_ERROR,
            )

        validate_analytical_requirement(self.requirement_id)
