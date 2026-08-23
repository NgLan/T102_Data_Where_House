"""Dependency Injection cho xác thực người dùng (Authentication Dependency)."""

from typing import Annotated

from config import get_settings
from fastapi import Depends, Security
from fastapi.security import APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.auth.auth_service import AuthService
from src.application.auth.i_auth_service import IAuthService
from src.application.auth.output import CurrentActorOutput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_revoked_token_repository import (
    PostgresRevokedTokenRepository,
)
from src.infrastructure.repositories.postgres_user_repository import (
    PostgresUserRepository,
)
from src.infrastructure.security.jwt_token_codec import JwtTokenCodec
from src.infrastructure.security.password_hasher import BcryptPasswordHasher
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork

AUTH_COOKIE_NAME = "p102_access_token"
cookie_scheme = APIKeyCookie(name=AUTH_COOKIE_NAME, auto_error=False)


def get_auth_service(
    session: AsyncSession = Depends(get_async_db_session),
) -> IAuthService:
    """Wiring Authentication service với repository và UoW cùng session."""
    return AuthService(
        users=PostgresUserRepository(session),
        revoked_tokens=PostgresRevokedTokenRepository(session),
        passwords=BcryptPasswordHasher(),
        tokens=JwtTokenCodec(
            get_settings().secret_key,
            get_settings().access_token_expire_minutes,
        ),
        unit_of_work=SqlAlchemyUnitOfWork(session),
    )


AuthServiceDependency = Annotated[IAuthService, Depends(get_auth_service)]
AuthTokenDependency = Annotated[str | None, Security(cookie_scheme)]


async def get_current_user(
    service: AuthServiceDependency,
    token: AuthTokenDependency,
) -> CurrentActorOutput:
    """Xác thực JWT HttpOnly cookie và trả actor hiện tại."""
    if token is None:
        raise BusinessException(
            ErrorCode.AUTHENTICATION_REQUIRED,
            "Vui lòng đăng nhập để tiếp tục.",
        )
    return await service.authenticate(token)


CurrentUserDependency = Annotated[
    CurrentActorOutput,
    Depends(get_current_user),
]
