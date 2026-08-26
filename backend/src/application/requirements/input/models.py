"""Input model cho các thao tác Requirement."""

from dataclasses import dataclass

from src.application.project_sessions.conversation_context import ConversationMemory
from src.domain.analytical_requirement.entities import AnalyticalRequirement
from src.domain.data_source.entities import DataSource
from src.domain.project_session.enums import RequirementContinuationAction
from src.domain.requirement.enums import RequirementPriority, RequirementType
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class ListRequirementsInput:
    """Dữ liệu đầu vào để liệt kê yêu cầu của một dự án."""

    project_id: EntityID


@dataclass(frozen=True, slots=True)
class DeleteRequirementInput:
    """Requirement thuộc Project cần xóa khỏi structured output."""

    project_id: EntityID
    requirement_id: EntityID


@dataclass(frozen=True, slots=True)
class RequirementContext:
    """Structured Requirement tối thiểu truyền cho RequirementAgent."""

    id: EntityID
    title: str
    description: str
    requirement_type: RequirementType
    priority: RequirementPriority


@dataclass(frozen=True, slots=True)
class RequirementDocumentContext:
    """Tên và extracted text của document dùng riêng trong Agent context."""

    name: str
    extracted_text: str


@dataclass(frozen=True, slots=True)
class ClarifyRequirementsInput:
    """Toàn bộ canonical context cho một lượt Requirement clarification."""

    raw_requirement: str
    documents: tuple[RequirementDocumentContext, ...]
    current_requirements: tuple[RequirementContext, ...]
    conversation: ConversationMemory


@dataclass(frozen=True, slots=True)
class DeriveAnalyticalRequirementsInput:
    """Approved requirements đủ semantic để derive phân tích."""

    requirements: tuple[RequirementContext, ...]


@dataclass(frozen=True, slots=True)
class EvaluateSourceCoverageInput:
    """Canonical input cho source coverage operation độc lập."""

    requirements: tuple[RequirementContext, ...]
    analytical_requirements: tuple[AnalyticalRequirement, ...]
    data_sources: tuple[DataSource, ...]


@dataclass(frozen=True, slots=True)
class GetRequirementClarificationInput:
    project_id: EntityID


@dataclass(frozen=True, slots=True)
class AnalyzeRequirementClarificationInput:
    project_id: EntityID
    expected_revision: int


@dataclass(frozen=True, slots=True)
class AnswerRequirementClarificationInput:
    project_id: EntityID
    session_id: EntityID
    question_id: EntityID
    option_index: int | None = None
    custom_answer: str | None = None


@dataclass(frozen=True, slots=True)
class SendRequirementClarificationMessageInput:
    """Tin nhắn follow-up trong Requirement session hiện hành."""

    project_id: EntityID
    session_id: EntityID
    expected_revision: int
    message: str


@dataclass(frozen=True, slots=True)
class ChooseRequirementContinuationInput:
    """Quyết định continuation cho Requirement session hiện hành."""

    project_id: EntityID
    session_id: EntityID
    action: RequirementContinuationAction
    expected_revision: int
