import os

os.environ["DEBUG"] = "false"

from main import app  # noqa: E402


def test_modeling_dashboard_endpoints_are_exported() -> None:
    paths = app.openapi()["paths"]
    assert "post" in paths["/api/v1/projects/{project_id}/data-model/validate"]
    assert set(paths["/api/v1/projects/{project_id}/sessions"]) == {
        "get",
        "post",
    }
    assert "get" in paths["/api/v1/sessions/{session_id}/events"]
    assert "get" in paths["/api/v1/sessions/{session_id}/events/stream"]
    assert "post" in paths["/api/v1/sessions/{session_id}/messages"]
    assert "get" in paths["/api/v1/sessions/{session_id}/clarification"]
    assert "post" in paths["/api/v1/sessions/{session_id}/clarifications/{question_id}/answer"]
    assert "get" in paths["/api/v1/sessions/{session_id}/pending-action"]
    assert "post" in paths[
        "/api/v1/sessions/{session_id}/pending-actions/{question_id}/decision"
    ]
    assert "get" in paths[
        "/api/v1/sessions/{session_id}/events/{tool_result_event_id}/artifact"
    ]


def test_agent_turn_contract_is_discriminated() -> None:
    document = app.openapi()
    response = document["paths"]["/api/v1/sessions/{session_id}/messages"]["post"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    wrapper_name = response["$ref"].rsplit("/", maxsplit=1)[-1]
    turn_schema = document["components"]["schemas"][wrapper_name]["properties"]["data"]["anyOf"][0]
    assert set(turn_schema["discriminator"]["mapping"]) == {
        "cancelled",
        "clarification",
        "confirmation_required",
        "no_change",
        "proposal",
        "tool_result",
    }
    assert len(turn_schema["oneOf"]) == 6
