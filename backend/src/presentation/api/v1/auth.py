"""REST endpoints cho register/login/me/logout bằng HttpOnly JWT cookie."""

from http import HTTPStatus

from config import get_settings
from fastapi import APIRouter, Response
from src.application.auth.output import AuthSessionOutput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.common.utils.datetime import utc_now
from src.presentation.dependencies.auth import (
    AUTH_COOKIE_NAME,
    AuthServiceDependency,
    AuthTokenDependency,
    CurrentUserDependency,
)
from src.presentation.dtos.auth.request import LoginRequest, RegisterRequest
from src.presentation.dtos.auth.response import CurrentActorResponse
from src.presentation.routing import ApiResponseRoute, error_responses

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    route_class=ApiResponseRoute,
)


@router.post(
    "/register",
    response_model=CurrentActorResponse,
    status_code=HTTPStatus.CREATED,
    operation_id="register",
    responses=error_responses(409, 422, 500),
)
async def register(
    request: RegisterRequest,
    response: Response,
    service: AuthServiceDependency,
) -> CurrentActorResponse:
    session = await service.register(request.to_application())
    _set_auth_cookie(response, session)
    return CurrentActorResponse.from_application(session.user)


@router.post(
    "/login",
    response_model=CurrentActorResponse,
    operation_id="login",
    responses=error_responses(401, 422, 500),
)
async def login(
    request: LoginRequest,
    response: Response,
    service: AuthServiceDependency,
) -> CurrentActorResponse:
    session = await service.login(request.to_application())
    _set_auth_cookie(response, session)
    return CurrentActorResponse.from_application(session.user)


@router.get(
    "/me",
    response_model=CurrentActorResponse,
    operation_id="getCurrentUser",
    responses=error_responses(401, 500),
)
async def get_current_actor(
    current_actor: CurrentUserDependency,
) -> CurrentActorResponse:
    """Trả hồ sơ user đã được JWT xác thực."""
    return CurrentActorResponse.from_application(current_actor)


@router.post(
    "/logout",
    status_code=HTTPStatus.NO_CONTENT,
    response_model=None,
    operation_id="logout",
    responses=error_responses(401, 500),
)
async def logout(
    token: AuthTokenDependency,
    service: AuthServiceDependency,
) -> Response:
    if token is None:
        raise BusinessException(ErrorCode.AUTHENTICATION_REQUIRED, "Vui lòng đăng nhập.")
    await service.logout(token)
    response = Response(status_code=HTTPStatus.NO_CONTENT)
    is_prod = get_settings().app_env == "production"
    response.delete_cookie(
        AUTH_COOKIE_NAME,
        path="/api/v1",
        secure=is_prod,
        httponly=True,
        samesite="none" if is_prod else "lax",
    )
    return response


def _set_auth_cookie(response: Response, session: AuthSessionOutput) -> None:
    settings = get_settings()
    max_age = max(int((session.expires_at - utc_now()).total_seconds()), 0)
    is_prod = settings.app_env == "production"
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=session.access_token,
        max_age=max_age,
        expires=session.expires_at,
        path="/api/v1",
        secure=is_prod,
        httponly=True,
        samesite="none" if is_prod else "lax",
    )
