from uuid import uuid4

import pytest
from src.application.project_sessions.conversation_context import ConversationTurn
from src.application.project_sessions.i_conversation_summary_agent import (
    ConversationSummaryInput,
)
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.project_session.conversation_summary import (
    ConversationSummary,
    SummaryDecision,
    SummaryItem,
)
from src.infrastructure.agents.conversation_summary_agent import ConversationSummaryAgent
from src.infrastructure.llm.conversation_summary_output import (
    ConversationSummaryOutput,
    ResolvedClarificationOutput,
    SummaryDecisionOutput,
    SummaryItemOutput,
)
from src.infrastructure.security.pii_guard import PiiGuard


class _StructuredModel:
    def __init__(self, result: ConversationSummaryOutput) -> None:
        self._result = result

    async def ainvoke(self, messages: list[object]) -> ConversationSummaryOutput:
        return self._result


class _ChatModel:
    def __init__(self, result: ConversationSummaryOutput) -> None:
        self._result = result

    def with_structured_output(self, schema: type) -> _StructuredModel:
        return _StructuredModel(self._result)


@pytest.mark.asyncio
async def test_summary_rejects_evidence_outside_previous_state_or_batch() -> None:
    turn = ConversationTurn(uuid4(), "user", uuid4(), "agent")
    output = ConversationSummaryOutput(
        current_goal=SummaryItemOutput(statement="goal", evidence_event_ids=[str(uuid4())])
    )
    agent = ConversationSummaryAgent(_ChatModel(output), PiiGuard(enabled=False))

    with pytest.raises(InfrastructureException) as caught:
        await agent.summarize(ConversationSummaryInput(None, (turn,), ()))

    assert caught.value.code is ErrorCode.LLM_STRUCTURED_OUTPUT_ERROR


def test_summary_schema_has_no_canonical_payload_fields() -> None:
    properties = ConversationSummaryOutput.model_json_schema()["properties"]

    assert "requirements" not in properties
    assert "analytical_requirements" not in properties
    assert "dbml" not in properties
    assert "schema_metadata" not in properties


@pytest.mark.asyncio
async def test_summary_retains_old_decision_when_new_dimension_is_added() -> None:
    old_event, user_event, agent_event = uuid4(), uuid4(), uuid4()
    previous = ConversationSummary(
        confirmed_decisions=(SummaryDecision("patient_count", "distinct patients", (old_event,)),)
    )
    output = ConversationSummaryOutput(
        confirmed_decisions=[
            SummaryDecisionOutput(
                key="patient_count",
                value="distinct patients",
                evidence_event_ids=[str(old_event)],
            ),
            SummaryDecisionOutput(
                key="dimension",
                value="department",
                evidence_event_ids=[str(user_event)],
            ),
        ]
    )
    turn = ConversationTurn(user_event, "add department", agent_event, "accepted")
    agent = ConversationSummaryAgent(_ChatModel(output), PiiGuard(enabled=False))

    result = await agent.summarize(ConversationSummaryInput(previous, (turn,), ()))

    assert {item.key for item in result.confirmed_decisions} == {
        "patient_count",
        "dimension",
    }


@pytest.mark.asyncio
async def test_summary_correction_replaces_old_active_value() -> None:
    old_event, user_event, agent_event = uuid4(), uuid4(), uuid4()
    previous = ConversationSummary(confirmed_decisions=(SummaryDecision("time_grain", "month", (old_event,)),))
    output = ConversationSummaryOutput(
        confirmed_decisions=[
            SummaryDecisionOutput(
                key="time_grain",
                value="quarter",
                evidence_event_ids=[str(user_event)],
            )
        ]
    )
    turn = ConversationTurn(user_event, "use quarter", agent_event, "accepted")
    agent = ConversationSummaryAgent(_ChatModel(output), PiiGuard(enabled=False))

    result = await agent.summarize(ConversationSummaryInput(previous, (turn,), ()))

    assert result.confirmed_decisions[0].value == "quarter"
    assert all(item.value != "month" for item in result.confirmed_decisions)


@pytest.mark.asyncio
async def test_resolved_question_becomes_decision_and_leaves_open_questions() -> None:
    question_event, answer_event, agent_event = uuid4(), uuid4(), uuid4()
    previous = ConversationSummary(open_questions=(SummaryItem("Count visits or patients?", (question_event,)),))
    output = ConversationSummaryOutput(
        confirmed_decisions=[
            SummaryDecisionOutput(
                key="patient_count",
                value="distinct patients",
                evidence_event_ids=[str(answer_event)],
            )
        ],
        resolved_clarifications=[
            ResolvedClarificationOutput(
                question="Count visits or patients?",
                answer="Distinct patients",
                question_event_id=str(question_event),
                answer_event_id=str(answer_event),
            )
        ],
    )
    turn = ConversationTurn(answer_event, "distinct", agent_event, "resolved")
    agent = ConversationSummaryAgent(_ChatModel(output), PiiGuard(enabled=False))

    result = await agent.summarize(ConversationSummaryInput(previous, (turn,), ()))

    assert result.open_questions == ()
    assert result.confirmed_decisions[0].value == "distinct patients"
