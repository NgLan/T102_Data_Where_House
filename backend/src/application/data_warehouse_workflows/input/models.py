"""Immutable input models cho Agent và workflow kho dữ liệu."""

from dataclasses import dataclass

from src.application.data_warehouse_workflows.output import ValidationIssue
from src.application.project_sessions.conversation_context import ConversationMemory
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.analytical_requirement.enums import SourceCoverageResolutionAction
from src.domain.data_source.entities import DataSource
from src.domain.requirement.entities import Requirement
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class GetAnalysisStatusInput:
    """Yêu cầu đọc trạng thái analysis của Project."""

    project_id: EntityID


@dataclass(frozen=True, slots=True)
class ReanalyzeProjectInput:
    """Yêu cầu phân tích lại input đã thay đổi."""

    project_id: EntityID


@dataclass(frozen=True, slots=True)
class GetSourceCoverageInput:
    """Yêu cầu reload persisted Source Coverage state."""

    project_id: EntityID


@dataclass(frozen=True, slots=True)
class ResolveSourceCoverageInput:
    """Resolve semantic ambiguity trên source revision hiện hành."""

    project_id: EntityID
    assessment_id: EntityID
    batch_id: EntityID
    expected_source_revision: int
    expected_resolution_revision: int
    action: SourceCoverageResolutionAction
    candidate_id: EntityID | None = None


@dataclass(frozen=True, slots=True)
class RecheckSourceCoverageInput:
    """Yêu cầu materialize toàn bộ câu trả lời và đánh giá lại một batch."""

    project_id: EntityID
    batch_id: EntityID
    expected_source_revision: int


@dataclass(frozen=True, slots=True)
class GenerateDataModelInput:
    """Yêu cầu tạo Data Model đầu tiên."""

    project_id: EntityID


@dataclass(frozen=True, slots=True)
class RegenerateDataModelInput:
    """Yêu cầu tạo lại và ghi đè Data Model hiện hành."""

    project_id: EntityID


@dataclass(frozen=True, slots=True)
class CreateAiEditProposalInput:
    """Yêu cầu AI chỉnh model và tạo Human Review proposal."""

    project_id: EntityID
    instruction: str


@dataclass(frozen=True, slots=True)
class CreateAgentTurnInput:
    """Yêu cầu Agent trả câu hỏi làm rõ hoặc proposal."""

    project_id: EntityID
    instruction: str
    memory: ConversationMemory
    turn_id: EntityID | None = None
    original_intent: str | None = None


@dataclass(frozen=True, slots=True)
class DataWarehouseDesignInput:
    """Input cho một lần gọi DWDesignAgent."""

    requirements: tuple[Requirement, ...]
    analytical_requirements: tuple[AnalyticalRequirement, ...]
    data_sources: tuple[DataSource, ...]
    failed_dbml: str | None = None
    validation_issues: tuple[ValidationIssue, ...] = ()


@dataclass(frozen=True, slots=True)
class RevisionDesignInput:
    """Input chỉnh sửa Data Model bằng DWDesignAgent."""

    requirements: tuple[Requirement, ...]
    analytical_requirements: tuple[AnalyticalRequirement, ...]
    data_sources: tuple[DataSource, ...]
    current_dbml: str
    instruction: str | None = None
    validation_issues: tuple[ValidationIssue, ...] = ()


@dataclass(frozen=True, slots=True)
class ConversationDesignInput:
    """Context đầy đủ cho một lượt hội thoại thiết kế kho dữ liệu."""

    revision: RevisionDesignInput
    memory: ConversationMemory
