"""REST endpoints cho Yêu cầu nghiệp vụ (Requirement) của dự án."""

from fastapi import APIRouter, status
from src.application.requirements.input import ListRequirementsInput
from src.presentation.dependencies.requirements import RequirementServiceDependency
from src.presentation.dtos.common import ApiErrorResponse
from src.presentation.dtos.requirements.request import (
    CreateRequirementRequest,
    ProjectIdPath,
)
from src.presentation.dtos.requirements.response import RequirementResponse
from src.presentation.routing import ApiResponseRoute

router = APIRouter(
    prefix="/projects/{project_id}/requirements",
    tags=["Requirements"],
    route_class=ApiResponseRoute,
)


@router.post(
    "",
    response_model=RequirementResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="createRequirement",
    responses={
        404: {"model": ApiErrorResponse},
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def create_requirement(
    project_id: ProjectIdPath,
    request: CreateRequirementRequest,
    service: RequirementServiceDependency,
) -> RequirementResponse:
    """Tạo mới một yêu cầu nghiệp vụ thô làm đầu vào cho RequirementAgent."""
    output = await service.create_requirement(request.to_application(project_id))
    return RequirementResponse.from_application(output)


@router.get(
    "",
    response_model=list[RequirementResponse],
    operation_id="listRequirements",
    responses={
        404: {"model": ApiErrorResponse},
        422: {"model": ApiErrorResponse},
        500: {"model": ApiErrorResponse},
    },
)
async def list_requirements(
    project_id: ProjectIdPath,
    service: RequirementServiceDependency,
) -> list[RequirementResponse]:
    """Liệt kê toàn bộ yêu cầu nghiệp vụ của dự án."""
    outputs = await service.list_requirements(ListRequirementsInput(project_id=project_id))
    return [RequirementResponse.from_application(item) for item in outputs]
