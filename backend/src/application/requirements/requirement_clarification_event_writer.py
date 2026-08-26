"""Persist canonical Requirement output and its session audit events."""

from dataclasses import dataclass

from src.application.project_sessions.session_event_factory import (
    AgentMessageEventInput,
    AgentResultEventInput,
    QuestionEventInput,
    create_agent_message,
    create_agent_result,
    create_question,
)
from src.application.requirements.output import RequirementClarificationResult
from src.application.requirements.requirement_clarification_dependencies import (
    RequirementClarificationDependencies,
)
from src.application.requirements.requirement_mapping import map_generated_requirements
from src.domain.project.entities import Project
from src.domain.project_session.entities import ProjectSession, SessionEvent
from src.domain.project_session.enums import (
    AgentResultStatus,
    RequirementClarificationStatus,
)


@dataclass(frozen=True, slots=True)
class RequirementTurnCompletionInput:
    """State đã lock cần để apply một Agent result."""

    session: ProjectSession
    call: SessionEvent
    result: RequirementClarificationResult
    project: Project
    requires_continuation_decision: bool = False


class RequirementClarificationEventWriter:
    """Write structured output, technical result và public response."""

    def __init__(self, dependencies: RequirementClarificationDependencies) -> None:
        self._dependencies = dependencies

    async def apply(self, data: RequirementTurnCompletionInput) -> None:
        await self._persist_canonical_requirements(data)
        technical = _success_event(data)
        await self._dependencies.events.save(technical)
        if data.result.status is RequirementClarificationStatus.NEEDS_CLARIFICATION:
            data.session.clear_continuation_decision()
            await self._persist_question(data)
        else:
            await self._persist_ready(data, technical)
        await self._dependencies.sessions.save(data.session)

    async def _persist_canonical_requirements(
        self, data: RequirementTurnCompletionInput
    ) -> None:
        current = await self._dependencies.requirements.list_by_project(data.project.id)
        entities = map_generated_requirements(
            data.project.id, data.result.requirements, tuple(current)
        )
        await self._dependencies.requirements.replace_by_project(
            data.project.id, entities
        )
        data.project.mark_requirement_analysis_completed()
        await self._dependencies.projects.save(data.project)

    async def _persist_ready(
        self, data: RequirementTurnCompletionInput, technical: SessionEvent
    ) -> None:
        data.session.release_turn(data.call.turn_id)
        if data.requires_continuation_decision:
            data.session.await_continuation_decision()
        else:
            data.session.clear_continuation_decision()
        await self._dependencies.events.save(
            create_agent_message(
                AgentMessageEventInput(
                    technical, data.result.summary or "Requirements are ready."
                )
            )
        )

    async def persist_failure(
        self, session: ProjectSession, call: SessionEvent
    ) -> None:
        session.release_turn(call.turn_id)
        await self._dependencies.sessions.save(session)
        await self._dependencies.events.save(
            create_agent_result(
                AgentResultEventInput(
                    call, AgentResultStatus.FAILED, "RequirementAgent turn failed."
                )
            )
        )

    async def archive_stale(
        self, session: ProjectSession, call: SessionEvent
    ) -> None:
        session.archive()
        await self._dependencies.sessions.save(session)
        await self._dependencies.events.save(
            create_agent_result(
                AgentResultEventInput(
                    call,
                    AgentResultStatus.CANCELLED,
                    "Requirement revision changed before Agent result was applied.",
                )
            )
        )

    async def _persist_question(self, data: RequirementTurnCompletionInput) -> None:
        if data.call.turn_id is None:
            raise ValueError("RequirementAgent call must have a turn ID.")
        result = data.result
        question = create_question(
            QuestionEventInput(
                data.session.id,
                data.call.turn_id,
                result.question or "Please clarify the requirement.",
                result.options,
                result.allow_custom_answer,
                result.reason,
                missing_information=result.reason,
            )
        )
        data.session.wait_for_clarification(data.call.turn_id, question.id)
        await self._dependencies.events.save(question)


def _success_event(data: RequirementTurnCompletionInput) -> SessionEvent:
    return create_agent_result(
        AgentResultEventInput(
            data.call,
            AgentResultStatus.SUCCESS,
            data.result.summary or "Requirement analysis completed.",
            f"revision={data.project.requirement_revision};status={data.result.status.value}",
        )
    )
