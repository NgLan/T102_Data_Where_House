from uuid import uuid4

import pytest
from src.application.data_warehouse_workflows.input import (
    ConversationDesignInput,
    RevisionDesignInput,
)
from src.application.project_sessions.conversation_context import (
    ConversationInputKind,
    ConversationMemory,
    ConversationTurn,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_source.entities import DataSource
from src.domain.data_source.value_objects import (
    ColumnMetadata,
    SchemaMetadata,
    TableMetadata,
)
from src.infrastructure.agents.conversation_context_builder import (
    ConversationContextBuilder,
)
from src.infrastructure.agents.conversation_token_policy import ConversationTokenPolicy
from src.infrastructure.llm.approximate_token_estimator import ApproximateTokenEstimator


def _turn(size: int) -> ConversationTurn:
    return ConversationTurn(uuid4(), "u" * size, uuid4(), "a" * size)


def _input(current: str, turns: tuple[ConversationTurn, ...]) -> ConversationDesignInput:
    memory = ConversationMemory(
        None,
        turns,
        current,
        ConversationInputKind.USER_MESSAGE,
    )
    revision = RevisionDesignInput((), (), (), "Table fact { id int [pk] }", current)
    return ConversationDesignInput(revision, memory)


def test_allocator_drops_whole_oldest_turn_before_mandatory_input() -> None:
    builder = ConversationContextBuilder(
        ConversationTokenPolicy(1200, 180), ApproximateTokenEstimator()
    )
    oldest = ConversationTurn(uuid4(), "oldest-" + "u" * 600, uuid4(), "a" * 600)
    data = _input("current-input-must-remain", (oldest, _turn(600), _turn(600)))

    built = builder.build(data, "system")

    assert built.dropped_turns > 0
    assert "current-input-must-remain" in built.user_prompt
    assert "oldest-" not in built.user_prompt


def test_prompt_uses_stable_canonical_summary_pending_history_current_order() -> None:
    builder = ConversationContextBuilder(
        ConversationTokenPolicy(8000, 1000), ApproximateTokenEstimator()
    )

    prompt = builder.build(_input("latest", (_turn(4),)), "system").user_prompt

    assert prompt.index("## Requirements") < prompt.index("## Cumulative conversation summary")
    assert prompt.index("## Cumulative conversation summary") < prompt.index("## Pending clarification")
    assert prompt.index("## Pending clarification") < prompt.index("## Recent completed")
    assert prompt.index("## Recent completed") < prompt.index("## Current user input")


def test_budget_error_keeps_mandatory_current_input_instead_of_truncating() -> None:
    builder = ConversationContextBuilder(
        ConversationTokenPolicy(200, 100), ApproximateTokenEstimator()
    )

    with pytest.raises(BusinessException) as caught:
        builder.build(_input("x" * 2000, ()), "system")

    assert caught.value.code is ErrorCode.CONVERSATION_CONTEXT_BUDGET_EXCEEDED


def test_projection_removes_profile_values_but_keeps_structural_keys_and_dbml() -> None:
    source = DataSource(
        project_id=uuid4(),
        name="orders",
        location="orders.csv",
        schema_metadata=SchemaMetadata(
            tables=(
                TableMetadata(
                    "orders",
                    (
                        ColumnMetadata(
                            "order_id",
                            "INTEGER",
                            primary_key=True,
                            distinct_values=("private-sample",),
                        ),
                    ),
                ),
            )
        ),
    )
    memory = ConversationMemory(
        None, (), "inspect orders", ConversationInputKind.USER_MESSAGE
    )
    revision = RevisionDesignInput(
        (), (), (source,), "Table fact { id int [pk] }", "inspect orders"
    )
    builder = ConversationContextBuilder(
        ConversationTokenPolicy(8000, 1000), ApproximateTokenEstimator()
    )

    built = builder.build(ConversationDesignInput(revision, memory), "system")

    assert "private-sample" not in built.user_prompt
    assert '"primary_key":true' in built.user_prompt
    assert "Table fact" in built.user_prompt
