"""Unit tests cho conservative structured-output normalization và repair."""

import pytest
from langchain_core.messages import AIMessage
from src.common.exceptions.infrastructure import InfrastructureException
from src.infrastructure.agents.structured_output_retry_reporting import (
    StructuredIssueLogContext,
    log_structured_issue,
    raise_structured_failure,
)
from src.infrastructure.llm.structured_output_decoder import decode_structured_payload
from src.infrastructure.llm.structured_output_models import (
    StructuredInvocationMetadata,
    StructuredOutputIssue,
)
from src.infrastructure.llm.structured_output_models import (
    StructuredOutputFailureCategory as Category,
)
from src.infrastructure.llm.structured_raw_response import extract_raw_text


@pytest.mark.parametrize(
    "raw",
    [
        '\ufeff  {"outcomes": []}',
        '```json\n{"outcomes": []}\n```',
        'Provider result: {"outcomes": []} end.',
    ],
)
def test_normalization_accepts_one_unambiguous_payload(raw: str) -> None:
    payload, issue = decode_structured_payload(raw, "stop")

    assert payload == {"outcomes": []}
    assert issue is None


@pytest.mark.parametrize(
    "raw",
    [
        '{"a": 1} {"b": 2}',
        '```json\n{"a": 1}\n``` trailing {"b": 2}',
    ],
)
def test_normalization_rejects_multiple_candidates(raw: str) -> None:
    payload, issue = decode_structured_payload(raw, "stop")

    assert payload is None
    assert issue is not None
    assert issue.category is Category.JSON_NORMALIZATION_FAILED


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('{"items": [1, 2,],}', {"items": [1, 2]}),
        ("{'items': [1, 2]}", {"items": [1, 2]}),
    ],
)
def test_guarded_repair_accepts_allowlisted_syntax(raw: str, expected: object) -> None:
    payload, issue = decode_structured_payload(raw, "stop")

    assert payload == expected, issue
    assert issue is None


@pytest.mark.parametrize(
    ("raw", "finish_reason"),
    [
        ('{"items": [1]}', "MAX_TOKENS"),
        ('{"items": ["cut', "stop"),
        ('{"items": [1', "stop"),
        ('{"item":}', "stop"),
    ],
)
def test_truncated_or_dangling_value_is_never_repaired(
    raw: str,
    finish_reason: str,
) -> None:
    payload, issue = decode_structured_payload(raw, finish_reason)

    assert payload is None
    assert issue is not None
    assert issue.category is Category.OUTPUT_TRUNCATED


def test_raw_tool_arguments_dict_is_available_for_item_recovery() -> None:
    raw = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "structured_output",
                "args": {"outcomes": []},
                "id": "call-1",
                "type": "tool_call",
            }
        ],
    )

    raw_text = extract_raw_text(raw)
    assert raw_text is not None
    assert decode_structured_payload(raw_text, "stop")[0] == {"outcomes": []}


def test_final_structured_failure_keeps_validation_cause() -> None:
    cause = ValueError("typed validation failed")
    issue = StructuredOutputIssue(
        Category.PYDANTIC_SCHEMA_ERROR,
        "Schema mismatch.",
        "R1",
        cause=cause,
    )

    with pytest.raises(InfrastructureException) as raised:
        raise_structured_failure(issue)

    assert raised.value.__cause__ is cause


def test_structured_issue_log_excludes_raw_payload(caplog: pytest.LogCaptureFixture) -> None:
    issue = StructuredOutputIssue(
        Category.SOURCE_COLUMN_UNKNOWN,
        "SECRET_RAW_PAYLOAD",
        "A2",
        "column_name",
    )
    context = StructuredIssueLogContext(
        "evaluate_source_coverage",
        2,
        StructuredInvocationMetadata("stop", "fake", "model"),
    )

    log_structured_issue(context, issue)

    assert "SECRET_RAW_PAYLOAD" not in caplog.text
    assert caplog.records[-1].transport_ref == "A2"
    assert caplog.records[-1].failure_category == "SOURCE_COLUMN_UNKNOWN"
