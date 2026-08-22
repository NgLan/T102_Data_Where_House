"""OpenAPI contract công khai của Project Init."""

import os

os.environ["DEBUG"] = "false"

from main import app  # noqa: E402


def test_structured_requirements_are_read_only() -> None:
    document = app.openapi()
    operations = document["paths"]["/api/v1/projects/{project_id}/requirements"]
    assert set(operations) == {"get"}


def test_data_source_analysis_contract_is_exported() -> None:
    schemas = app.openapi()["components"]["schemas"]
    assert schemas["DataSourceAnalysisStatus"]["enum"] == ["PENDING", "READY"]
    assert "CATEGORY" in schemas["ColumnDataType"]["enum"]
    assert "analysis_status" in schemas["DataSourceResponse"]["properties"]
    assert "total_files_uploaded" in schemas["UploadDataSourcesResponse"]["properties"]
    column_properties = schemas["DataSourceColumnResponse"]["properties"]
    assert {"is_unique_candidate", "is_key_candidate"} <= set(column_properties)
