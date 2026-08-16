"""Contract tests cho năm Project endpoints và OpenAPI schema."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from main import app
from src.application.projects.i_project_service import IProjectService
from src.application.projects.input import CreateProjectInput, ListProjectsInput, ProjectIdInput, UpdateProjectInput
from src.application.projects.output import ProjectOutput, ProjectSummaryOutput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.project.enums import ProjectStatus
from src.presentation.dependencies.projects import get_project_service
from typing_extensions import override

FORBIDDEN_ID = UUID("00000000-0000-0000-0000-000000000403")
MISSING_ID = UUID("00000000-0000-0000-0000-000000000404")
FAILING_ID = UUID("00000000-0000-0000-0000-000000000500")


class StubProjectService(IProjectService):
    """Service stub xác nhận router chỉ map contract và payload."""

    def __init__(self) -> None:
        self.project = make_project_output()

    @override
    async def create_project(self, data: CreateProjectInput) -> ProjectOutput:
        self.project = make_project_output(name=data.name, requirement=data.requirement)
        return self.project

    @override
    async def list_projects(self, data: ListProjectsInput) -> tuple[ProjectSummaryOutput, ...]:
        del data
        return (make_summary(self.project),)

    @override
    async def get_project(self, data: ProjectIdInput) -> ProjectOutput:
        raise_for_test_id(data.project_id)
        return self.project

    @override
    async def update_project(self, data: UpdateProjectInput) -> ProjectOutput:
        raise_for_test_id(data.project_id)
        self.project = make_project_output(name=data.name, requirement=data.requirement)
        return self.project

    @override
    async def delete_project(self, data: ProjectIdInput) -> None:
        raise_for_test_id(data.project_id)


@pytest_asyncio.fixture
async def project_client():
    """HTTP client với Project composition dependency được cô lập."""
    service = StubProjectService()
    app.dependency_overrides[get_project_service] = lambda: service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.pop(get_project_service, None)


@pytest.mark.asyncio
async def test_project_endpoints_have_expected_runtime_contract(project_client: AsyncClient) -> None:
    """Năm operations trả đúng status và success envelope duy nhất."""
    body = {"name": "Sales project", "requirement": "Theo dõi doanh thu", "domain": "retail"}
    created = await project_client.post("/api/v1/projects", json=body)
    listed = await project_client.get("/api/v1/projects")
    project_id = created.json()["data"]["id"]
    fetched = await project_client.get(f"/api/v1/projects/{project_id}")
    updated = await project_client.put(f"/api/v1/projects/{project_id}", json=body)
    deleted = await project_client.delete(f"/api/v1/projects/{project_id}")
    assert [created.status_code, listed.status_code, fetched.status_code, updated.status_code, deleted.status_code] == [
        201,
        200,
        200,
        200,
        204,
    ]
    assert created.json()["data"]["name"] == "Sales project"
    assert isinstance(listed.json()["data"], list)
    assert "data" not in created.json()["data"]
    assert deleted.content == b""


@pytest.mark.asyncio
async def test_project_validation_and_known_errors_are_standardized(project_client: AsyncClient) -> None:
    """Unknown field, 403, 404 và 500 dùng error envelope chuẩn."""
    invalid = await project_client.post(
        "/api/v1/projects",
        json={
            "name": "ab",
            "requirement": "short",
            "unknown": True,
        },
    )
    nested_source = await project_client.put(
        f"/api/v1/projects/{uuid4()}",
        json={
            "name": "Sales project",
            "requirement": "Theo dõi doanh thu",
            "data_sources": [],
        },
    )
    forbidden = await project_client.get(f"/api/v1/projects/{FORBIDDEN_ID}")
    missing = await project_client.get(f"/api/v1/projects/{MISSING_ID}")
    failing = await project_client.get(f"/api/v1/projects/{FAILING_ID}")
    assert invalid.status_code == 422 and invalid.json()["details"]
    assert nested_source.status_code == 422 and nested_source.json()["details"]
    assert forbidden.json()["error_code"] == "PERMISSION_DENIED"
    assert missing.json()["error_code"] == "PROJECT_NOT_FOUND"
    assert failing.status_code == 500 and failing.json()["error_code"] == "DATABASE_ERROR"


def test_project_openapi_has_stable_operations_and_concrete_envelopes() -> None:
    """OpenAPI công bố đủ operations, 204 và không lồng ApiResponse."""
    schema = app.openapi()
    paths = schema["paths"]
    assert paths["/api/v1/projects"]["post"]["operationId"] == "createProject"
    assert paths["/api/v1/projects"]["get"]["operationId"] == "listProjects"
    item = paths["/api/v1/projects/{project_id}"]
    assert [item[method]["operationId"] for method in ("get", "put", "delete")] == [
        "getProject",
        "updateProject",
        "deleteProject",
    ]
    assert "204" in item["delete"]["responses"]
    create_ref = paths["/api/v1/projects"]["post"]["responses"]["201"]["content"]["application/json"]["schema"]["$ref"]
    assert "ApiResponse_ProjectResponse_" in create_ref
    components = schema["components"]["schemas"]
    assert "data_sources" not in components["CreateProjectRequest"]["properties"]
    assert "data_sources" not in components["UpdateProjectRequest"]["properties"]
    summary_properties = components["ProjectSummaryResponse"]["properties"]
    assert "data_source_count" in summary_properties
    assert "data_source_ids" not in summary_properties


def make_project_output(name: str = "Project", requirement: str = "Yêu cầu hợp lệ") -> ProjectOutput:
    now = datetime.now(UTC)
    return ProjectOutput(uuid4(), name, requirement, uuid4(), ProjectStatus.ACTIVE, "retail", None, now, now, 0, ())


def make_summary(project: ProjectOutput) -> ProjectSummaryOutput:
    return ProjectSummaryOutput(
        project.id,
        project.name,
        project.requirement,
        project.user_id,
        project.status,
        project.domain,
        project.description,
        project.created_at,
        project.updated_at,
        project.data_source_count,
    )


def raise_for_test_id(project_id: UUID) -> None:
    if project_id == FORBIDDEN_ID:
        raise BusinessException(ErrorCode.PERMISSION_DENIED, "Không có quyền.")
    if project_id == MISSING_ID:
        raise BusinessException(ErrorCode.PROJECT_NOT_FOUND, "Không tồn tại.")
    if project_id == FAILING_ID:
        raise InfrastructureException(ErrorCode.DATABASE_ERROR, "Database error.")
