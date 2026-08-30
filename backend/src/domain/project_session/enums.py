"""Các kiểu liệt kê (Enums) thuộc miền Phiên Agent (Agent Session)."""

from enum import StrEnum


class SessionStatus(StrEnum):
    """Trạng thái phiên làm việc (Project Session Status)."""

    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class SessionPurpose(StrEnum):
    """Mục đích nghiệp vụ của Project Session."""

    REQUIREMENT_CLARIFICATION = "REQUIREMENT_CLARIFICATION"
    DATA_MODELING = "DATA_MODELING"


class RequirementClarificationStatus(StrEnum):
    """Trạng thái hiển thị của Requirement clarification cycle."""

    IDLE = "IDLE"
    PROCESSING = "PROCESSING"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    READY = "READY"


class RequirementContinuationState(StrEnum):
    """Quyết định tiếp tục workflow sau một clarification turn READY."""

    NOT_REQUIRED = "NOT_REQUIRED"
    AWAITING_DECISION = "AWAITING_DECISION"
    CONTINUE_EDITING = "CONTINUE_EDITING"
    CONTINUE_ANALYSIS = "CONTINUE_ANALYSIS"


class RequirementContinuationAction(StrEnum):
    """Action công khai mà owner được chọn tại continuation gate."""

    CONTINUE_EDITING = "CONTINUE_EDITING"
    CONTINUE_ANALYSIS = "CONTINUE_ANALYSIS"


class SessionEventRole(StrEnum):
    """Vai trò khởi tạo sự kiện trong phiên."""

    USER = "USER"
    AGENT = "AGENT"
    TOOL = "TOOL"


class SessionEventType(StrEnum):
    """Loại sự kiện diễn ra trong phiên."""

    MESSAGE = "MESSAGE"
    QUESTION = "QUESTION"
    ANSWER = "ANSWER"
    AGENT_CALL = "AGENT_CALL"
    AGENT_RESULT = "AGENT_RESULT"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"


class ClarificationAnswerKind(StrEnum):
    """Cách người dùng trả lời một clarification."""

    OPTION = "OPTION"
    CUSTOM = "CUSTOM"


class SessionQuestionKind(StrEnum):
    """Discriminator cho question cũ và các bước xác nhận tool."""

    CLARIFICATION = "CLARIFICATION"
    SANDBOX_MODE_SELECTION = "SANDBOX_MODE_SELECTION"
    TOOL_CONFIRMATION = "TOOL_CONFIRMATION"


class AgentType(StrEnum):
    """Danh sách 4 Agent hợp lệ trong hệ thống."""

    ORCHESTRATOR = "OrchestratorAgent"
    REQUIREMENT = "RequirementAgent"
    DATA_SOURCE = "DataSourceAgent"
    DW_DESIGN = "DWDesignAgent"


class AgentResultStatus(StrEnum):
    """Trạng thái kết quả thực thi của Agent (SUCCESS, FAILED, CANCELLED)."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ToolResultStatus(StrEnum):
    """Trạng thái kết quả thực thi của Tool (SUCCESS, FAILED)."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
