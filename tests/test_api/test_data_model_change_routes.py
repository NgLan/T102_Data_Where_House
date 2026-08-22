"""API contract tests cho Data Model artifacts và change proposals."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from main import app
from src.application.data_models.i_data_model_service import IDataModelService
from src.application.data_models.output import (
    ChangeProposalDetailOutput,
    ChangeProposalSummaryOutput,
    DataModelOutput,
)
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataWarehouseWorkflowService,
)
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.data_model.enums import DataModelChangeStatus
from src.presentation.dependencies.data_models import get_data_model_service
from src.presentation.dependencies.data_warehouse_workflows import get_data_warehouse_workflow

DBML = "Table users {\n  id int [pk]\n}"
PROPOSED_DBML = "Table users {\n  id int [pk]\n  email varchar\n}"


def proposal_outputs():
    now = datetime.now(UTC)
    model_id, change_id, actor_id = uuid4(), uuid4(), uuid4()
    summary = ChangeProposalSummaryOutput(
        change_id,
        model_id,
        actor_id,
        3,
        DataModelChangeStatus.PROPOSED,
        now,
        now,
    )
    detail = ChangeProposalDetailOutput(summary, PROPOSED_DBML, DBML, 3, False)
    return summary, detail


@pytest.fixture
def data_model_service():
    service = AsyncMock(spec=IDataModelService)
    app.dependency_overrides[get_data_model_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


@pytest.fixture
def workflow_service():
    """Override workflow dependency cho endpoint AI revision."""
    service = AsyncMock(spec=IDataWarehouseWorkflowService)
    app.dependency_overrides[get_data_warehouse_workflow] = lambda: service
    yield service
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_change_proposal_preserves_payload(client, data_model_service) -> None:
    summary, detail = proposal_outputs()
    project_id = uuid4()
    data_model_service.get_change_proposal.return_value = detail

    fetched = await client.get(
        f"/api/v1/projects/{project_id}/data-model-changes/{summary.id}"
    )

    assert fetched.json()["data"]["proposed_dbml"] == PROPOSED_DBML
    assert fetched.json()["data"]["current_dbml"] == DBML


@pytest.mark.asyncio
async def test_ai_revision_request_maps_to_consolidated_service(
    client, workflow_service
) -> None:
    _, detail = proposal_outputs()
    project_id = uuid4()
    workflow_service.create_ai_edit_proposal.return_value = detail

    response = await client.post(
        f"/api/v1/projects/{project_id}/data-model/proposals/ai-edit",
        json={"instruction": "thêm cột email"},
    )

    assert response.status_code == 200
    data = workflow_service.create_ai_edit_proposal.await_args.args[0]
    assert data.project_id == project_id
    assert data.instruction == "thêm cột email"


@pytest.mark.asyncio
async def test_accept_and_reject_use_same_service(client, data_model_service) -> None:
    summary, _ = proposal_outputs()
    now = datetime.now(UTC)
    data_model_service.accept_change_proposal.return_value = DataModelOutput(
        summary.data_model_id, uuid4(), PROPOSED_DBML, 4, now, now
    )
    rejected = ChangeProposalSummaryOutput(
        summary.id,
        summary.data_model_id,
        summary.user_id,
        summary.base_revision,
        DataModelChangeStatus.REJECTED,
        summary.created_at,
        now,
    )
    data_model_service.reject_change_proposal.return_value = rejected

    accepted_response = await client.post(
        f"/api/v1/data-model-changes/{summary.id}/accept"
    )
    rejected_response = await client.post(
        f"/api/v1/data-model-changes/{summary.id}/reject"
    )

    assert accepted_response.json()["data"]["revision"] == 4
    assert rejected_response.json()["data"]["status"] == "REJECTED"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("code", "status"),
    [(ErrorCode.AUTHENTICATION_REQUIRED, 401), (ErrorCode.PERMISSION_DENIED, 403)],
)
async def test_authorization_errors_are_standardized(
    client, data_model_service, code: ErrorCode, status: int
) -> None:
    data_model_service.get_data_model.side_effect = BusinessException(code, "denied")

    response = await client.get(f"/api/v1/projects/{uuid4()}/data-model")

    assert response.status_code == status
    assert response.json()["error_code"] == code.value
