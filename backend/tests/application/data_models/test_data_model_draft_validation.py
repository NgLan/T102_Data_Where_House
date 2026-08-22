from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.application.data_models.data_model_service import DataModelService
from src.application.data_models.input import ValidateDataModelInput
from src.application.data_warehouse_workflows.output import (
    ValidationIssue,
    ValidationIssueCode,
    ValidationSeverity,
)


@pytest.mark.asyncio
async def test_validate_draft_only_uses_deterministic_validator() -> None:
    project_id = uuid4()
    issue = ValidationIssue(
        severity=ValidationSeverity.WARNING,
        code=ValidationIssueCode.TABLE_PRIMARY_KEY_MISSING,
        title="Missing primary key",
        description="Table has no primary key.",
    )
    models = MagicMock()
    changes = MagicMock()
    validator = MagicMock()
    validator.validate.return_value = (issue,)
    unit_of_work = MagicMock()
    access = MagicMock()
    access.require_member = AsyncMock()
    service = DataModelService(
        models,
        changes,
        validator,
        unit_of_work,
        access,
        MagicMock(),
    )

    result = await service.validate_draft(
        ValidateDataModelInput(project_id, "Table users { id int [pk] }")
    )

    assert result == (issue,)
    access.require_member.assert_awaited_once_with(project_id)
    validator.validate.assert_called_once_with("Table users { id int [pk] }")
    models.assert_not_called()
    changes.assert_not_called()
    unit_of_work.assert_not_called()
