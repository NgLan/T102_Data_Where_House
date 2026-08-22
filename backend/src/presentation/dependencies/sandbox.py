"""Composition root của Sandbox application service."""

from typing import Annotated

from config import get_settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.sandbox.i_sandbox_service import ISandboxService
from src.application.sandbox.sandbox_service import SandboxService
from src.infrastructure.database.session import get_async_db_session
from src.infrastructure.repositories.postgres_sandbox_config_repository import (
    PostgresSandboxConfigRepository,
)
from src.infrastructure.sandbox.sandbox_executor import PostgresSandboxExecutor
from src.infrastructure.security.credential_cipher import CredentialCipher
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from src.presentation.dependencies.project_access import ProjectAccessDependency


def get_sandbox_service(
    access: ProjectAccessDependency,
    session: AsyncSession = Depends(get_async_db_session),
) -> ISandboxService:
    """Wiring Sandbox service với actor và transaction hiện tại."""
    return SandboxService(
        configs=PostgresSandboxConfigRepository(
            session,
            CredentialCipher(get_settings().secret_key),
        ),
        unit_of_work=SqlAlchemyUnitOfWork(session),
        executor=PostgresSandboxExecutor(),
        access=access,
    )


SandboxServiceDependency = Annotated[
    ISandboxService,
    Depends(get_sandbox_service),
]
