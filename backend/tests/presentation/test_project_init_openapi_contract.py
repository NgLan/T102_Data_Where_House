"""OpenAPI contract công khai của Project Init."""

import os

os.environ["DEBUG"] = "false"

from main import app  # noqa: E402


def test_structured_requirements_support_delete_only() -> None:
    document = app.openapi()
    operations = document["paths"]["/api/v1/projects/{project_id}/requirements"]
    assert set(operations) == {"get"}
    item_operations = document["paths"][
        "/api/v1/projects/{project_id}/requirements/{requirement_id}"
    ]
    assert set(item_operations) == {"delete"}


def test_data_source_analysis_contract_is_exported() -> None:
    schemas = app.openapi()["components"]["schemas"]
    assert schemas["DataSourceAnalysisStatus"]["enum"] == ["PENDING", "READY"]
    assert "CATEGORY" in schemas["ColumnDataType"]["enum"]
    assert "analysis_status" in schemas["DataSourceResponse"]["properties"]
    assert "total_files_uploaded" in schemas["UploadDataSourcesResponse"]["properties"]
    column_properties = schemas["DataSourceColumnResponse"]["properties"]
    assert {"is_unique_candidate", "is_key_candidate"} <= set(column_properties)


def test_requirement_clarification_contract_is_exported() -> None:
    document = app.openapi()
    paths = document["paths"]
    prefix = "/api/v1/projects/{project_id}"
    assert paths[f"{prefix}/requirement"]["put"]["operationId"] == (
        "saveProjectRawRequirement"
    )
    assert "get" in paths[f"{prefix}/requirement-files"]
    assert "post" in paths[f"{prefix}/requirement-files/upload"]
    assert paths[f"{prefix}/requirement-clarification"]["get"]["operationId"] == (
        "getProjectRequirementClarification"
    )
    assert f"{prefix}/requirement-clarification/analyze" in paths
    message_path = f"{prefix}/requirement-clarification/{{session_id}}/messages"
    assert paths[message_path]["post"]["operationId"] == (
        "sendProjectRequirementClarificationMessage"
    )
    continuation_path = (
        f"{prefix}/requirement-clarification/{{session_id}}/continuation"
    )
    assert paths[continuation_path]["post"]["operationId"] == (
        "chooseProjectRequirementContinuation"
    )
    response_properties = document["components"]["schemas"][
        "RequirementClarificationResponse"
    ]["properties"]
    assert "continuation_state" in response_properties
    assert f"{prefix}/requirement-clarification/{{session_id}}/confirm" not in paths
    assert paths[f"{prefix}/initialize"]["post"]["operationId"] == (
        "runProjectInitializationWorkflow"
    )


def test_session_contract_requires_purpose_and_can_filter_conversation() -> None:
    document = app.openapi()
    paths = document["paths"]
    sessions = paths["/api/v1/projects/{project_id}/sessions"]["get"]
    purpose = next(item for item in sessions["parameters"] if item["name"] == "purpose")
    assert purpose["required"] is True
    events = paths["/api/v1/sessions/{session_id}/events"]["get"]
    assert any(item["name"] == "conversation_only" for item in events["parameters"])
    properties = document["components"]["schemas"]["ProjectSessionResponse"]["properties"]
    assert {"purpose", "base_requirement_revision"} <= set(properties)


def test_source_coverage_contract_is_typed_in_openapi() -> None:
    document = app.openapi()
    schemas, paths = document["components"]["schemas"], document["paths"]
    prefix = "/api/v1/projects/{project_id}/source-coverage"
    assert paths[prefix]["get"]["operationId"] == "getProjectSourceCoverage"
    resolution = f"{prefix}/{{assessment_id}}/resolution"
    assert paths[resolution]["post"]["operationId"] == "resolveProjectSourceCoverage"
    assert paths[f"{prefix}/recheck"]["post"]["operationId"] == "recheckProjectSourceCoverage"
    assessment = schemas["SourceCoverageAssessmentResponse"]["properties"]
    assert {
        "coverage_status", "confirmation_status", "required_concept_key",
        "title", "explanation", "question", "resolution_revision", "candidates",
    } <= set(assessment)
    batch = schemas["SourceCoverageBatchResponse"]["properties"]
    assert {"id", "confirmation_total", "confirmation_resolved", "can_recheck"} <= set(batch)
    assert "suggested_source_fields" not in str(document)
