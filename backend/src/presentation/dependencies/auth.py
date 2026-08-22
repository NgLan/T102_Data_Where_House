"""Dependency Injection cho xác thực người dùng (Authentication Dependency)."""

from typing import Annotated

from config import get_settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.auth.auth_service import AuthService
from src.application.auth.i_auth_service import IAuthService
from src.application.auth.input import ResolveCurrentActorInput
from src.application.auth.output import CurrentActorOutput
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_user_repository import (
    PostgresUserRepository,
)
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


def get_auth_service(
    session: AsyncSession = Depends(get_async_db_session),
) -> IAuthService:
    """Wiring Authentication service với repository và UoW cùng session."""
    return AuthService(
        users=PostgresUserRepository(session),
        unit_of_work=SqlAlchemyUnitOfWork(session),
    )


async def get_current_user(
    service: Annotated[IAuthService, Depends(get_auth_service)],
) -> CurrentActorOutput:
    """Resolve danh tính MVP qua Authentication application service."""
    settings = get_settings()
    return await service.resolve_current_actor(
        ResolveCurrentActorInput(
            user_id=settings.mvp_actor_id,
            username=settings.mvp_actor_username,
            email=settings.mvp_actor_email,
        )
    )


CurrentUserDependency = Annotated[
    CurrentActorOutput,
    Depends(get_current_user),
]
