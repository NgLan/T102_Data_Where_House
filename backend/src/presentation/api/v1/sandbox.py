"""REST endpoints cho Quản lý Sandbox và Chạy thử DDL."""

from uuid import UUID

from fastapi import APIRouter, Path
from src.application.sandbox.input import (
    ExecuteSandboxDdlInput,
    GetSandboxConfigInput,
    SaveSandboxConfigInput,
    TestSandboxConnectionInput,
)
from src.presentation.dependencies.sandbox import SandboxServiceDependency
from src.presentation.dtos.sandbox.request import (
    ExecuteDdlRequest,
    SandboxConfigRequest,
    TestConnectionRequest,
)
from src.presentation.dtos.sandbox.response import (
    ExecuteDdlResponse,
    SandboxConfigResponse,
    TestConnectionResponse,
)
from src.presentation.routing import ApiResponseRoute, error_responses

router = APIRouter(
    prefix="",
    tags=["Sandbox"],
    route_class=ApiResponseRoute,
)


@router.get(
    "/projects/{project_id}/sandbox/config",
    response_model=SandboxConfigResponse | None,
    operation_id="getSandboxConfig",
    responses=error_responses(401, 403, 404, 500),
)
async def get_sandbox_config(
    service: SandboxServiceDependency,
    project_id: UUID = Path(..., description="ID dự án"),
) -> SandboxConfigResponse | None:
    """Lấy cấu hình Sandbox DB của dự án."""
    output = await service.get_config(GetSandboxConfigInput(project_id))
    return SandboxConfigResponse.from_application(output) if output else None


@router.post(
    "/projects/{project_id}/sandbox/config",
    response_model=SandboxConfigResponse,
    operation_id="saveSandboxConfig",
    responses=error_responses(401, 403, 422, 500),
)
async def save_sandbox_config(
    request: SandboxConfigRequest,
    service: SandboxServiceDependency,
    project_id: UUID = Path(..., description="ID dự án"),
) -> SandboxConfigResponse:
    """Lưu hoặc cập nhật thông tin cấu hình Sandbox DB cho dự án."""
    output = await service.save_config(SaveSandboxConfigInput(project_id, request.to_application()))
    return SandboxConfigResponse.from_application(output)


@router.post(
    "/projects/{project_id}/sandbox/test-connection",
    response_model=TestConnectionResponse,
    operation_id="testSandboxConnection",
    responses=error_responses(400, 401, 403, 404, 422, 500),
)
async def test_sandbox_connection_endpoint(
    request: TestConnectionRequest,
    service: SandboxServiceDependency,
    project_id: UUID = Path(..., description="ID dự án"),
) -> TestConnectionResponse:
    """Kiểm tra thử kết nối đến cơ sở dữ liệu Sandbox."""
    output = await service.test_connection(TestSandboxConnectionInput(project_id, request.to_application()))
    return TestConnectionResponse.from_application(output)


@router.post(
    "/projects/{project_id}/sandbox/execute-ddl",
    response_model=ExecuteDdlResponse,
    operation_id="executeSandboxDdl",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def execute_sandbox_ddl_endpoint(
    request: ExecuteDdlRequest,
    service: SandboxServiceDependency,
    project_id: UUID = Path(..., description="ID dự án"),
) -> ExecuteDdlResponse:
    """Thực thi mã DDL script trên Sandbox Database đã cấu hình của dự án."""
    output = await service.execute_ddl(ExecuteSandboxDdlInput(project_id, request.ddl_script, request.reset_schema))
    return ExecuteDdlResponse.from_application(output)
