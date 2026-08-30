"""Fail-closed intent routing cho các Agent tool rõ ràng."""

import re

from src.application.agent_tools.models import AgentToolIntent, AgentToolName, AgentToolRequest
from src.application.data_models.input import DataModelTargetInput
from src.domain.data_model.enums import DataModelTargetKind
from src.domain.sandbox.enums import SandboxDbType
from src.domain.shared.types import EntityID


def parse_agent_tool_intent(project_id: EntityID, content: str, locale: str = "vi") -> AgentToolIntent | None:
    """Chỉ route câu có action/tool marker rõ; còn lại để DWDesignAgent xử lý."""
    text = content.casefold()
    target = DataModelTargetInput(
        DataModelTargetKind.PROPOSAL if _contains(text, "proposal", "đề xuất") else DataModelTargetKind.CURRENT_MODEL
    )
    if _contains(text, "tài liệu phân tích", "analysis document", "file giải thích"):
        request = AgentToolRequest(project_id, AgentToolName.GENERATE_ANALYSIS, target, locale=locale)
        return AgentToolIntent(request)
    if _contains(text, "kiểm tra kết nối", "test connection"):
        request = AgentToolRequest(project_id, AgentToolName.TEST_SANDBOX_CONNECTION, target)
        return AgentToolIntent(request)
    if _contains(text, "cấu hình sandbox", "sandbox config") and _contains(text, "xem", "show", "get"):
        request = AgentToolRequest(project_id, AgentToolName.GET_SANDBOX_CONFIG, target)
        return AgentToolIntent(request)
    if _contains(text, "chạy thử", "run sandbox", "execute sandbox", "sandbox đi"):
        reset = True if _contains(text, "reset schema", "xóa schema") else None
        if _contains(text, "không reset", "giữ nguyên schema", "without reset"):
            reset = False
        request = AgentToolRequest(
            project_id, AgentToolName.EXECUTE_SANDBOX_DDL, target, SandboxDbType.POSTGRESQL, reset, locale
        )
        return AgentToolIntent(request, True)
    if _contains(text, "xuất sql", "tải sql", "file sql", "tạo ddl", "generate ddl"):
        request = AgentToolRequest(project_id, AgentToolName.GENERATE_DDL, target, _dialect(text), locale=locale)
        return AgentToolIntent(request)
    return None


def _dialect(text: str) -> SandboxDbType:
    aliases = {
        "mysql": SandboxDbType.MYSQL,
        "sqlite": SandboxDbType.SQLITE,
        "sql server": SandboxDbType.SQLSERVER,
        "bigquery": SandboxDbType.BIGQUERY,
        "snowflake": SandboxDbType.SNOWFLAKE,
    }
    return next((value for key, value in aliases.items() if key in text), SandboxDbType.POSTGRESQL)


def _contains(text: str, *patterns: str) -> bool:
    return any(re.search(rf"\b{re.escape(pattern)}\b", text) for pattern in patterns)
