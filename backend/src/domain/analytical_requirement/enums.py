"""Các kiểu liệt kê (Enums) thuộc miền Yêu cầu Phân tích (Analytical Requirement)."""

from enum import StrEnum


class AggregationMethod(StrEnum):
    """Phương thức tổng hợp dữ liệu (SUM, AVG, COUNT, MAX, MIN...)."""

    SUM = "SUM"
    AVG = "AVG"
    COUNT = "COUNT"
    COUNT_DISTINCT = "COUNT_DISTINCT"
    MAX = "MAX"
    MIN = "MIN"


class SourceCoverageStatus(StrEnum):
    """Mức sẵn sàng của một khái niệm nghiệp vụ so với source hiện tại."""

    SUPPORTED = "SUPPORTED"
    NEEDS_SOURCE_CONFIRMATION = "NEEDS_SOURCE_CONFIRMATION"
    MISSING_SOURCE = "MISSING_SOURCE"


class SourceCandidateKind(StrEnum):
    """Loại bằng chứng source có thể ánh xạ tới một business concept."""

    COLUMN = "COLUMN"
    RELATIONSHIP = "RELATIONSHIP"


class SourceCoverageResolutionAction(StrEnum):
    """Hành động có cấu trúc để resolve một coverage assessment."""

    CONFIRM_CANDIDATE = "CONFIRM_CANDIDATE"
    REJECT_ALL_CANDIDATES = "REJECT_ALL_CANDIDATES"


class SourceConfirmationStatus(StrEnum):
    """Trạng thái câu trả lời của một confirmation item trong batch hiện hành."""

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
