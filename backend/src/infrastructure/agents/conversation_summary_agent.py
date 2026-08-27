"""Provider-neutral structured Agent cho cumulative conversation summary."""

import json
from dataclasses import asdict
from uuid import UUID

from src.application.project_sessions.i_conversation_summary_agent import (
    ConversationSummaryInput,
    IConversationSummaryAgent,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.project_session.conversation_summary import (
    ConversationSummary,
    ResolvedClarification,
    SummaryDecision,
    SummaryItem,
)
from src.infrastructure.agents.conversation_summary_validation import (
    require_allowed_event_id,
    validate_canonical_references,
)
from src.infrastructure.agents.prompts.conversation_summary import (
    CONVERSATION_SUMMARY_SYSTEM_PROMPT,
    CONVERSATION_SUMMARY_USER_PROMPT,
)
from src.infrastructure.llm.conversation_summary_output import (
    ConversationSummaryOutput,
    SummaryDecisionOutput,
    SummaryItemOutput,
)
from src.infrastructure.llm.lazy_chat_model import LazyLlmGateway, LlmGatewaySource
from src.infrastructure.llm.structured_llm_invoker import StructuredLlmInvoker
from src.infrastructure.security.pii_guard import PiiGuard
from typing_extensions import override


class ConversationSummaryAgent(IConversationSummaryAgent):
    """Compact đúng một batch thành toàn bộ structured current state."""

    def __init__(self, gateway: LlmGatewaySource, pii_guard: PiiGuard) -> None:
        self._gateway = LazyLlmGateway(gateway)
        self._pii_guard = pii_guard

    @override
    async def summarize(self, data: ConversationSummaryInput) -> ConversationSummary:
        prompt = _render_prompt(data)
        result = await StructuredLlmInvoker(self._gateway.get(), self._pii_guard).invoke(
            CONVERSATION_SUMMARY_SYSTEM_PROMPT,
            prompt,
            ConversationSummaryOutput,
        )
        try:
            return _to_domain(
                result,
                _allowed_evidence_ids(data),
                frozenset(data.canonical_context_index),
            )
        except (BusinessException, ValueError) as exc:
            raise InfrastructureException(
                ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR,
                "Conversation summary chứa evidence hoặc canonical reference không hợp lệ.",
            ) from exc


def _render_prompt(data: ConversationSummaryInput) -> str:
    return CONVERSATION_SUMMARY_USER_PROMPT.format(
        canonical_index=json.dumps(data.canonical_context_index, ensure_ascii=False),
        previous_summary=json.dumps(
            asdict(data.previous_summary) if data.previous_summary else None,
            default=str,
            ensure_ascii=False,
        ),
        turns=json.dumps([asdict(turn) for turn in data.turns], default=str),
        allowed_evidence_ids=json.dumps(sorted(str(item) for item in _allowed_evidence_ids(data))),
    )


def _allowed_evidence_ids(data: ConversationSummaryInput) -> frozenset[UUID]:
    event_ids = {event_id for turn in data.turns for event_id in (turn.user_event_id, turn.agent_event_id)}
    if data.previous_summary:
        event_ids.update(_summary_evidence(data.previous_summary))
    return frozenset(event_ids)


def _summary_evidence(summary: ConversationSummary) -> set[UUID]:
    items = tuple(filter(None, (summary.current_goal, summary.current_task)))
    items += summary.important_constraints + summary.open_questions
    items += summary.rejected_assumptions
    evidence = {event_id for item in items for event_id in item.evidence_event_ids}
    evidence.update(event_id for item in summary.confirmed_decisions for event_id in item.evidence_event_ids)
    for item in summary.resolved_clarifications:
        evidence.update((item.question_event_id, item.answer_event_id))
    return evidence


def _to_domain(
    output: ConversationSummaryOutput,
    allowed: frozenset[UUID],
    canonical_index: frozenset[str],
) -> ConversationSummary:
    references = validate_canonical_references(output, canonical_index)
    return ConversationSummary(
        current_goal=_item(output.current_goal, allowed),
        confirmed_decisions=tuple(_decision(item, allowed) for item in output.confirmed_decisions),
        resolved_clarifications=tuple(
            ResolvedClarification(
                item.question,
                item.answer,
                require_allowed_event_id(item.question_event_id, allowed),
                require_allowed_event_id(item.answer_event_id, allowed),
            )
            for item in output.resolved_clarifications
        ),
        important_constraints=tuple(_item(item, allowed) for item in output.important_constraints),
        current_task=_item(output.current_task, allowed),
        open_questions=tuple(_item(item, allowed) for item in output.open_questions),
        rejected_assumptions=tuple(_item(item, allowed) for item in output.rejected_assumptions),
        canonical_references=references,
    )


def _item(item: SummaryItemOutput | None, allowed: frozenset[UUID]) -> SummaryItem | None:
    if item is None:
        return None
    return SummaryItem(
        item.statement,
        tuple(require_allowed_event_id(value, allowed) for value in item.evidence_event_ids),
    )


def _decision(item: SummaryDecisionOutput, allowed: frozenset[UUID]) -> SummaryDecision:
    return SummaryDecision(
        item.key,
        item.value,
        tuple(require_allowed_event_id(value, allowed) for value in item.evidence_event_ids),
    )
