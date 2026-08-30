"""Safe payload conversion for persisted Agent tool events."""

from src.application.agent_tools import AgentToolName, AgentToolRequest, AgentToolResult
from src.application.data_models.input import DataModelTargetInput
from src.domain.data_model.enums import DataModelTargetKind
from src.domain.project_session.clarification import ClarificationQuestionMetadata
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.sandbox.enums import SandboxDbType


def require_tool_question(event: SessionEvent) -> ClarificationQuestionMetadata:
    if not isinstance(event.metadata, ClarificationQuestionMetadata):
        raise ValueError("Question metadata is invalid.")
    return event.metadata


def request_from_question(session: ProjectSession, metadata: ClarificationQuestionMetadata) -> AgentToolRequest:
    if not metadata.tool_name:
        raise ValueError("Tool question is missing a tool name.")
    target = DataModelTargetInput(
        metadata.target_kind or DataModelTargetKind.CURRENT_MODEL,
        metadata.proposal_change_id,
    )
    return AgentToolRequest(
        session.project_id,
        AgentToolName(metadata.tool_name),
        target,
        metadata.db_type or SandboxDbType.POSTGRESQL,
        metadata.reset_schema,
        expected_revision=metadata.expected_revision,
    )


def safe_tool_arguments(request: AgentToolRequest) -> dict[str, object]:
    return {
        "target_kind": request.target.kind,
        "proposal_change_id": request.target.change_id,
        "db_type": request.db_type,
        "reset_schema": request.reset_schema,
        "expected_revision": request.expected_revision,
    }


def safe_tool_result(result: AgentToolResult) -> dict[str, object]:
    payload = _execution_projection(result)
    if result.artifact:
        payload.update(_artifact_projection(result))
    return payload


def _execution_projection(result: AgentToolResult) -> dict[str, object]:
    return {
        "summary": result.summary,
        "endpoint_risk": result.endpoint_risk,
        "schema_name": result.schema_name,
        "executed_statements": result.executed_statements,
        "succeeded_statements": result.succeeded_statements,
        "failed_statements": result.failed_statements,
        "total_duration_ms": result.total_duration_ms,
    }


def _artifact_projection(result: AgentToolResult) -> dict[str, object]:
    artifact = result.artifact
    if artifact is None:
        return {}
    return {
        "artifact_id": artifact.id,
        "filename": artifact.filename,
        "storage_path": artifact.storage_filename,
        "mime_type": artifact.mime_type,
        "data_model_revision": artifact.data_model_revision,
        "target_kind": artifact.target_kind,
        "proposal_change_id": artifact.proposal_change_id,
        "current_revision": artifact.current_revision,
        "base_revision": artifact.base_revision,
    }
