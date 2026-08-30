"""Dependency bundle for generic session clarification."""

from dataclasses import dataclass

from src.application.agent_tools import IAgentToolService
from src.application.common.unit_of_work import IUnitOfWork
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataWarehouseWorkflowService,
)
from src.application.project_sessions.conversation_summary_compactor import (
    ConversationSummaryCompactor,
)
from src.application.project_sessions.session_access import OwnedSessionAccess
from src.domain.project_session.i_project_session_repository import (
    IProjectSessionRepository,
)
from src.domain.project_session.i_session_event_repository import ISessionEventRepository


@dataclass(frozen=True, slots=True)
class ClarificationDependencies:
    """Collaborators shared by clarification start and completion."""

    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    workflow: IDataWarehouseWorkflowService
    unit_of_work: IUnitOfWork
    access: OwnedSessionAccess
    context: ConversationSummaryCompactor
    tools: IAgentToolService | None = None
