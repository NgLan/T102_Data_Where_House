"""Điều phối synchronous batch compaction ngoài database transaction."""

from dataclasses import dataclass

from src.application.common.unit_of_work import IUnitOfWork
from src.application.project_sessions.conversation_canonical_index import (
    ConversationCanonicalIndexReader,
)
from src.application.project_sessions.conversation_context import (
    ConversationMemory,
    ConversationTurn,
    group_conversation_turns,
)
from src.application.project_sessions.conversation_context_policy import (
    ConversationContextPolicy,
    ConversationMemoryInput,
)
from src.application.project_sessions.i_conversation_summary_agent import (
    ConversationSummaryInput,
    IConversationSummaryAgent,
)
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.logging import get_logger
from src.common.utils.datetime import utc_now
from src.domain.project_session.conversation_summary import (
    ConversationSummary,
    ConversationSummaryUpdate,
)
from src.domain.project_session.entities import ProjectSession
from src.domain.project_session.i_project_session_repository import (
    IProjectSessionRepository,
)
from src.domain.project_session.i_session_event_repository import (
    ConversationEventQuery,
    ISessionEventRepository,
)
from src.domain.shared.types import EntityID

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class SummaryCompactorDependencies:
    """Dependencies cho read, LLM compaction và checkpoint persistence."""

    sessions: IProjectSessionRepository
    events: ISessionEventRepository
    agent: IConversationSummaryAgent
    canonical_index: ConversationCanonicalIndexReader
    unit_of_work: IUnitOfWork
    policy: ConversationContextPolicy

class ConversationSummaryCompactor:
    """Tạo summary checkpoint và dựng bounded conversational memory dùng chung."""

    def __init__(self, dependencies: SummaryCompactorDependencies) -> None:
        self._dependencies = dependencies

    async def build_memory(self, data: ConversationMemoryInput) -> ConversationMemory:
        await self.compact_if_needed(data.session_id, data.project_id)
        session = await self._require_session(data.session_id)
        turns = await self._turns_after_checkpoint(session)
        return ConversationMemory(
            session.conversation_summary,
            turns[-self._dependencies.policy.recent_turns :],
            data.current_input,
            data.input_kind,
            data.pending,
        )

    async def compact_if_needed(self, session_id: EntityID, project_id: EntityID) -> bool:
        session = await self._require_session(session_id)
        turns = await self._turns_after_checkpoint(session)
        batch = self._compaction_batch(turns)
        if not batch:
            return False
        canonical_index = await self._dependencies.canonical_index.read(project_id)
        await self._dependencies.unit_of_work.rollback()
        summary = await self._dependencies.agent.summarize(
            ConversationSummaryInput(
                session.conversation_summary,
                batch,
                canonical_index,
            )
        )
        return await self._persist_if_current(session, summary, batch[-1].agent_event_id)

    async def compact_after_completion(
        self, session_id: EntityID, project_id: EntityID
    ) -> None:
        """Giữ turn đã persist thành công khi derived summary tạm thời thất bại."""
        try:
            await self.compact_if_needed(session_id, project_id)
        except InfrastructureException:
            logger.exception(
                "conversation_summary_compaction_failed session_id=%s", session_id
            )

    async def _require_session(self, session_id: EntityID) -> ProjectSession:
        session = await self._dependencies.sessions.get_by_id(session_id)
        if session is None:
            raise ValueError("Project session disappeared during context compaction.")
        return session

    async def _turns_after_checkpoint(
        self, session: ProjectSession
    ) -> tuple[ConversationTurn, ...]:
        events = await self._dependencies.events.list_conversation_events(
            ConversationEventQuery(session.id, session.summarized_through_event_id)
        )
        return group_conversation_turns(events)

    def _compaction_batch(
        self, turns: tuple[ConversationTurn, ...]
    ) -> tuple[ConversationTurn, ...]:
        policy = self._dependencies.policy
        checkpoint_size = policy.recent_turns + policy.summary_batch_size
        if len(turns) < checkpoint_size:
            return ()
        return turns[: policy.summary_batch_size]

    async def _persist_if_current(
        self,
        snapshot: ProjectSession,
        summary: ConversationSummary,
        through_event_id: EntityID,
    ) -> bool:
        dependencies = self._dependencies
        async with dependencies.unit_of_work:
            current = await dependencies.sessions.get_by_id_for_update(snapshot.id)
            if current is None:
                raise ValueError("Project session disappeared during summary persistence.")
            if current.summarized_through_event_id != snapshot.summarized_through_event_id:
                return False
            current.apply_conversation_summary(ConversationSummaryUpdate(summary, through_event_id, utc_now()))
            await dependencies.sessions.save(current)
            await dependencies.unit_of_work.commit()
        return True
