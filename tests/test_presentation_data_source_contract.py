"""Presentation contract tests cho typed Data Source column metadata."""


import pytest
from main import app
from pydantic import ValidationError
from src.domain.data_source.enums import ColumnConstraintType, ColumnDataType
from src.presentation.dtos.data_sources.request import UpdateDataSourceColumnRequest


def test_column_patch_requires_at_least_one_field() -> None:
    """PATCH rỗng bị chặn ngay tại HTTP DTO boundary."""
    with pytest.raises(ValidationError):
        UpdateDataSourceColumnRequest()


def test_column_patch_accepts_discriminated_constraint_union() -> None:
    """Constraint được phân nhánh bằng type và không nhận field thừa."""
    request = UpdateDataSourceColumnRequest.model_validate(
        {
            "data_type": "CATEGORY",
            "distinct_values": ["new", "done"],
            "constraints": [
                {"type": "CHECK", "expression": "status <> ''"},
                {"type": "DEFAULT", "value": "new"},
            ],
        }
    )

    assert request.data_type is ColumnDataType.CATEGORY
    assert request.constraints is not None
    assert request.constraints[0].type is ColumnConstraintType.CHECK

    with pytest.raises(ValidationError):
        UpdateDataSourceColumnRequest.model_validate(
            {"constraints": [{"type": "UNIQUE", "expression": "unexpected"}]}
        )


def test_openapi_exposes_nested_column_path_and_new_enum() -> None:
    """OpenAPI chỉ công bố path lồng nhau và enum data type mới."""
    schema = app.openapi()
    path = "/api/v1/projects/{project_id}/data-sources/{source_id}/tables/{table_name}/columns/{column_name}"

    assert schema["paths"][path]["patch"]["operationId"] == "updateProjectDataSourceColumn"
    values = schema["components"]["schemas"]["ColumnDataType"]["enum"]
    assert values == [
        "TEXT",
        "CATEGORY",
        "INTEGER",
        "NUMBER",
        "DECIMAL",
        "DATE",
        "TIME",
        "DATETIME",
        "BOOLEAN",
    ]
