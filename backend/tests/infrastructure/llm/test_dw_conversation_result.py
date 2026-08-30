import pytest
from pydantic import ValidationError
from src.application.data_warehouse_workflows.output import AgentTurnKind
from src.infrastructure.agents.conversation_result_mapper import to_conversation_result
from src.infrastructure.llm.agent_structured_outputs import DwConversationResult


def test_no_change_result_does_not_require_dbml() -> None:
    result = DwConversationResult(
        kind="no_change",
        question=None,
        options=[],
        allow_custom_answer=False,
        reason=None,
        dbml=None,
        summary="The current model already satisfies the request.",
    )

    assert result.kind == "no_change"
    assert result.dbml is None


def test_no_change_result_rejects_generated_dbml() -> None:
    with pytest.raises(ValidationError):
        DwConversationResult(
            kind="no_change",
            question=None,
            options=[],
            allow_custom_answer=False,
            reason=None,
            dbml="Table unnecessary { id int [pk] }",
            summary="No change is needed.",
        )


def test_tool_request_is_typed_and_contains_no_schema_payload() -> None:
    result = DwConversationResult(
        kind="tool_request",
        question=None,
        options=[],
        allow_custom_answer=False,
        reason=None,
        dbml=None,
        summary="Preparing the PostgreSQL DDL artifact.",
        tool_name="generate_data_model_ddl",
        target_kind="CURRENT_MODEL",
        db_type="POSTGRESQL",
    )

    mapped = to_conversation_result(result)

    assert mapped.kind is AgentTurnKind.TOOL_REQUEST
    assert mapped.tool_request is not None
    assert mapped.tool_request.name == "generate_data_model_ddl"
    assert result.dbml is None
