"""Kiểm thử CRUD dùng chung và dịch lỗi persistence."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import OperationalError
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.user.entities import User
from src.domain.user.value_objects import Email
from src.infrastructure.database.error_translation import translate_database_errors
from src.infrastructure.database.mappers.user_mapper import UserMapper
from src.infrastructure.database.models.user import UserModel
from src.infrastructure.repositories.sqlalchemy_crud import SqlAlchemyCrud


@pytest.mark.asyncio
async def test_generic_crud_saves_and_loads_entity() -> None:
    session = MagicMock()
    session.get = AsyncMock(return_value=None)
    session.flush = AsyncMock()
    crud = SqlAlchemyCrud(session, UserModel, UserMapper)
    user = User(username="tester", email=Email("tester@example.com"))

    saved = await crud.save(user)

    assert saved.id == user.id
    session.add.assert_called_once()
    session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_database_error_translation_preserves_exception_chain() -> None:
    database_error = OperationalError("select 1", {}, RuntimeError("driver failed"))

    @translate_database_errors
    async def failing_operation() -> None:
        raise database_error

    with pytest.raises(InfrastructureException) as exc_info:
        await failing_operation()

    assert exc_info.value.__cause__ is database_error


def test_mapper_update_keeps_created_at_immutable() -> None:
    original = User(username="before", email=Email("before@example.com"))
    model = UserMapper.to_model(original)
    created_at = model.created_at
    changed = User(
        id=original.id,
        username="after",
        email=Email("after@example.com"),
        created_at=original.created_at,
    )

    UserMapper.update_model(model, changed)

    assert model.created_at == created_at
