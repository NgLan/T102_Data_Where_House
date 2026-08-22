"""REST endpoint cho danh tính actor MVP hiện tại."""

from fastapi import APIRouter
from src.presentation.dependencies.auth import CurrentUserDependency
from src.presentation.dtos.auth.response import CurrentActorResponse
from src.presentation.routing import ApiResponseRoute, error_responses

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    route_class=ApiResponseRoute,
)


@router.get(
    "/me",
    response_model=CurrentActorResponse,
    operation_id="getCurrentActor",
    responses=error_responses(401, 500),
)
async def get_current_actor(
    current_actor: CurrentUserDependency,
) -> CurrentActorResponse:
    """Trả danh tính actor MVP đang được backend sử dụng."""
    return CurrentActorResponse.from_application(current_actor)
