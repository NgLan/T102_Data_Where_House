"""REST endpoints cho Project Management."""

from http import HTTPStatus

from fastapi import APIRouter, Response
from src.application.projects.input import ListProjectsInput, ProjectIdInput
from src.presentation.dependencies.projects import ProjectServiceDependency
from src.presentation.dtos.common import ApiErrorResponse
from src.presentation.dtos.projects.request import (
    CreateProjectRequest,
    ProjectIdPath,
    UpdateProjectRequest,
)
from src.presentation.dtos.projects.response import (
    ProjectResponse,
    ProjectSummaryResponse,
)
from src.presentation.routing import ApiResponseRoute, ErrorResponses

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    route_class=ApiResponseRoute,
)

COMMON_ERROR_RESPONSES: ErrorResponses = {
    401: {"model": ApiErrorResponse},
    422: {"model": ApiErrorResponse},
    500: {"model": ApiErrorResponse},
}
AUTHORIZED_ERROR_RESPONSES: ErrorResponses = {
    403: {"model": ApiErrorResponse},
    404: {"model": ApiErrorResponse},
    **COMMON_ERROR_RESPONSES,
}


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=HTTPStatus.CREATED,
    operation_id="createProject",
    responses=COMMON_ERROR_RESPONSES,
)
async def create_project(
    request: CreateProjectRequest,
    service: ProjectServiceDependency,
) -> ProjectResponse:
    """Tạo Project và OWNER membership trong một transaction."""
    output = await service.create_project(request.to_application())
    return ProjectResponse.from_project(output)


@router.get(
    "",
    response_model=list[ProjectSummaryResponse],
    operation_id="listProjects",
    responses=COMMON_ERROR_RESPONSES,
)
async def list_projects(
    service: ProjectServiceDependency,
) -> list[ProjectSummaryResponse]:
    """Liệt kê Project mà người dùng hiện tại được phép truy cập."""
    outputs = await service.list_projects(ListProjectsInput())
    return [ProjectSummaryResponse.from_summary(item) for item in outputs]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    operation_id="getProject",
    responses=AUTHORIZED_ERROR_RESPONSES,
)
async def get_project(
    project_id: ProjectIdPath,
    service: ProjectServiceDependency,
) -> ProjectResponse:
    """Lấy chi tiết một Project sau khi kiểm tra membership."""
    output = await service.get_project(ProjectIdInput(project_id=project_id))
    return ProjectResponse.from_project(output)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    operation_id="updateProject",
    responses=AUTHORIZED_ERROR_RESPONSES,
)
async def update_project(
    project_id: ProjectIdPath,
    request: UpdateProjectRequest,
    service: ProjectServiceDependency,
) -> ProjectResponse:
    """Thay thế thông tin Project do OWNER sở hữu."""
    output = await service.update_project(request.to_application(project_id))
    return ProjectResponse.from_project(output)


@router.delete(
    "/{project_id}",
    status_code=HTTPStatus.NO_CONTENT,
    response_model=None,
    operation_id="deleteProject",
    responses=AUTHORIZED_ERROR_RESPONSES,
)
async def delete_project(
    project_id: ProjectIdPath,
    service: ProjectServiceDependency,
) -> Response:
    """Xóa Project do OWNER sở hữu cùng toàn bộ artifact liên quan."""
    await service.delete_project(ProjectIdInput(project_id=project_id))
    return Response(status_code=HTTPStatus.NO_CONTENT)
