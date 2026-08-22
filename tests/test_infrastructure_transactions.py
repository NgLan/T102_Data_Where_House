"""Kiểm thử quyền sở hữu transaction của Unit of Work."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from src.infrastructure.database import session as session_module
from src.infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_uow_commits_exactly_once_without_exit_rollback() -> None:
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    async with SqlAlchemyUnitOfWork(session) as unit_of_work:
        await unit_of_work.commit()

    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_uow_rolls_back_when_scope_exits_uncommitted() -> None:
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    async with SqlAlchemyUnitOfWork(session):
        pass

    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_session_dependency_never_commits(monkeypatch) -> None:
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    class SessionContext:
        async def __aenter__(self):
            return session

        async def __aexit__(self, *_args):
            return None

    monkeypatch.setattr(session_module, "get_async_session_factory", lambda: SessionContext)
    dependency = session_module.get_async_db_session()
    assert await anext(dependency) is session
    await dependency.aclose()

    session.commit.assert_not_awaited()
    session.rollback.assert_not_awaited()
