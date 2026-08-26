import pytest
from pydantic import ValidationError
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
