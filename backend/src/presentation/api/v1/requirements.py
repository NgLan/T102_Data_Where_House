"""REST endpoints cho Yêu cầu nghiệp vụ (Requirement) của dự án."""

from fastapi import APIRouter
from src.application.requirements.input import DeleteRequirementInput, ListRequirementsInput
from src.presentation.dependencies.requirements import RequirementServiceDependency
from src.presentation.dtos.requirements.request import ProjectIdPath, RequirementIdPath
from src.presentation.dtos.requirements.response import RequirementResponse
from src.presentation.routing import ApiResponseRoute, error_responses

router = APIRouter(
    prefix="/projects/{project_id}/requirements",
    tags=["Requirements"],
    route_class=ApiResponseRoute,
)


@router.get(
    "",
    response_model=list[RequirementResponse],
    operation_id="listRequirements",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def list_requirements(
    project_id: ProjectIdPath,
    service: RequirementServiceDependency,
) -> list[RequirementResponse]:
    """Liệt kê toàn bộ yêu cầu nghiệp vụ của dự án."""
    outputs = await service.list_requirements(ListRequirementsInput(project_id=project_id))
    return [RequirementResponse.from_application(item) for item in outputs]


@router.delete(
    "/{requirement_id}",
    response_model=None,
    status_code=204,
    operation_id="deleteRequirement",
    responses=error_responses(401, 403, 404, 422, 500),
)
async def delete_requirement(
    project_id: ProjectIdPath,
    requirement_id: RequirementIdPath,
    service: RequirementServiceDependency,
) -> None:
    """Xóa một Structured Requirement sai khỏi kết quả hiện hành."""
    await service.delete_requirement(DeleteRequirementInput(project_id, requirement_id))

