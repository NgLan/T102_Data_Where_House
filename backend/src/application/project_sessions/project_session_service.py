"""Application service for persisted project Agent sessions."""

from dataclasses import dataclass

from src.application.agent_tools import IAgentToolService
from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataWarehouseWorkflowService,
)
from src.application.project_sessions.clarification_output import ClarificationQuestionOutput
from src.application.project_sessions.conversation_summary_compactor import (
    ConversationSummaryCompactor,
)
from src.application.project_sessions.i_project_session_service import (
    IProjectSessionService,
)
from src.application.project_sessions.input import (
    AnswerClarificationInput,
    CreateSessionInput,
    GetPendingClarificationInput,
    GetSessionInput,
    GetToolArtifactInput,
    ListSessionEventsInput,
    ListSessionsInput,
    RenameSessionInput,
    SendSessionMessageInput,
)
from src.application.project_sessions.output import (
    ProjectSessionOutput,
    SessionEventOutput,
    SessionTurnOutput,
    ToolArtifactDownloadOutput,
)
from src.application.project_sessions.session_access import OwnedSessionAccess
from src.application.project_sessions.session_clarification_coordinator import (
    ClarificationDependencies,
    SessionClarificationCoordinator,
)
from src.application.project_sessions.session_turn_coordinator import (
    SessionTurnCoordinator,
    SessionTurnDependencies,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.json import safe_json_loads
from src.domain.project_session.entities import DEFAULT_SESSION_TITLE, ProjectSession, SessionEvent
from src.domain.project_session.enums import SessionEventType, SessionPurpose
from src.domain.project_session.i_project_session_repository import (
    IProjectSessionRepository,
)
from src.domain.project_session.i_session_event_repository import (
    ISessionEventRepository,
)
from src.domain.project_session.value_objects import ToolResultMetadata
from typing_extensions import override


@dataclass(frozen=True, slots=True)
class ProjectSessionDependencies:
    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    workflow: IDataWarehouseWorkflowService
    unit_of_work: IUnitOfWork
    access: ProjectAccessPolicy
    context: ConversationSummaryCompactor
    tools: IAgentToolService | None = None


class ProjectSessionService(IProjectSessionService):
    def __init__(self, dependencies: ProjectSessionDependencies) -> None:
        self._sessions = dependencies.sessions
        self._events = dependencies.events
        self._unit_of_work = dependencies.unit_of_work
        self._projects = dependencies.access
        self._tools = dependencies.tools
        self._access = OwnedSessionAccess(dependencies.sessions, dependencies.access)
        self._turns = _build_turn_coordinator(dependencies, self._access)
        self._clarifications = _build_clarification_coordinator(dependencies, self._access)

    @override
    async def create_session(self, data: CreateSessionInput) -> ProjectSessionOutput:
        if data.purpose is not SessionPurpose.DATA_MODELING:
            raise BusinessException(
                ErrorCode.SESSION_PURPOSE_MISMATCH,
                "Requirement sessions chỉ được tạo bởi clarification workflow.",
            )
        await self._projects.require_owner(data.project_id)
        session = ProjectSession(
            project_id=data.project_id,
            user_id=self._projects.actor_id,
            title=data.title or DEFAULT_SESSION_TITLE,
            purpose=data.purpose,
        )
        async with self._unit_of_work:
            saved = await self._sessions.save(session)
            await self._unit_of_work.commit()
        return ProjectSessionOutput.from_domain(saved)

    @override
    async def list_sessions(self, data: ListSessionsInput) -> tuple[ProjectSessionOutput, ...]:
        await self._projects.require_owner(data.project_id)
        sessions = await self._sessions.list_by_project_user_and_purpose(
            data.project_id, self._projects.actor_id, data.purpose
        )
        return tuple(ProjectSessionOutput.from_domain(item) for item in sessions)

    @override
    async def get_session(self, data: GetSessionInput) -> ProjectSessionOutput:
        session = await self._access.require(data.session_id)
        return ProjectSessionOutput.from_domain(session)

    @override
    async def rename_session(self, data: RenameSessionInput) -> ProjectSessionOutput:
        session = await self._access.require(data.session_id)
        session.rename(data.title)
        async with self._unit_of_work:
            saved = await self._sessions.save(session)
            await self._unit_of_work.commit()
        return ProjectSessionOutput.from_domain(saved)

    @override
    async def list_events(self, data: ListSessionEventsInput) -> tuple[SessionEventOutput, ...]:
        if data.conversation_only:
            await self._access.require_conversation_reader(data.session_id)
            from src.domain.project_session.i_session_event_repository import ConversationEventQuery

            events = await self._events.list_conversation_events(ConversationEventQuery(data.session_id, data.after_id))
            events = events[: data.limit]
        else:
            await self._access.require(data.session_id)
            events = await self._events.list_by_session(data.session_id, data.after_id, data.limit)
        return tuple(SessionEventOutput.from_domain(item) for item in events)

    @override
    async def send_message(self, data: SendSessionMessageInput) -> SessionTurnOutput:
        return await self._turns.send(data)

    @override
    async def get_pending_clarification(self, data: GetPendingClarificationInput) -> ClarificationQuestionOutput | None:
        return await self._clarifications.get_pending(data)

    @override
    async def answer_clarification(self, data: AnswerClarificationInput) -> SessionTurnOutput:
        return await self._clarifications.answer(data)

    @override
    async def get_tool_artifact(self, data: GetToolArtifactInput) -> ToolArtifactDownloadOutput:
        await self._access.require(data.session_id)
        event = await self._events.get_by_id(data.tool_result_event_id)
        payload = _require_artifact_payload(event, data.session_id)
        if self._tools is None:
            _raise_artifact_not_found()
        content = await self._tools.read_artifact(str(payload["storage_path"]))
        return ToolArtifactDownloadOutput(str(payload["filename"]), str(payload["mime_type"]), content)


def _require_artifact_payload(event: SessionEvent | None, session_id: object) -> dict:
    if (
        event is None
        or event.session_id != session_id
        or event.type is not SessionEventType.TOOL_RESULT
        or not isinstance(event.metadata, ToolResultMetadata)
    ):
        _raise_artifact_not_found()
    payload = safe_json_loads(event.metadata.result_data or "{}")
    required = ("storage_path", "filename", "mime_type")
    if not isinstance(payload, dict) or not all(payload.get(key) for key in required):
        _raise_artifact_not_found()
    return payload


def _raise_artifact_not_found() -> None:
    raise BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "Không tìm thấy artifact của tool.")


def _build_turn_coordinator(data: ProjectSessionDependencies, access: OwnedSessionAccess) -> SessionTurnCoordinator:
    dependencies = SessionTurnDependencies(
        data.sessions,
        data.events,
        data.workflow,
        data.unit_of_work,
        access,
        data.context,
        data.tools,
    )
    return SessionTurnCoordinator(dependencies)


def _build_clarification_coordinator(
    data: ProjectSessionDependencies, access: OwnedSessionAccess
) -> SessionClarificationCoordinator:
    dependencies = ClarificationDependencies(
        data.sessions,
        data.events,
        data.workflow,
        data.unit_of_work,
        access,
        data.context,
        data.tools,
    )
    return SessionClarificationCoordinator(dependencies)
