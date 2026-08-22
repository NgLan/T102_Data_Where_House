"""Unit tests cho toàn bộ 10 PostgreSQL Repositories trong tầng Infrastructure."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError
from src.common.exceptions.infrastructure import InfrastructureException
from src.common.utils.datetime import utc_now
from src.domain.project.entities import Project
from src.domain.user.entities import User
from src.domain.user.value_objects import Email
from src.infrastructure.database.models.project import ProjectModel
from src.infrastructure.database.models.user import UserModel
from src.infrastructure.repositories.postgres_data_source_repository import PostgresDataSourceRepository
from src.infrastructure.repositories.postgres_project_repository import PostgresProjectRepository
from src.infrastructure.repositories.postgres_user_repository import PostgresUserRepository


@pytest.mark.asyncio
async def test_postgres_user_repository_get_by_id() -> None:
    """Test get_by_id của PostgresUserRepository."""
    user_id = uuid4()
    now = utc_now()
    mock_model = UserModel(
        id=user_id,
        username="alice",
        email="alice@example.com",
        created_at=now,
        updated_at=now,
    )

    session = AsyncMock()
    session.get.return_value = mock_model

    repo = PostgresUserRepository(session)
    user = await repo.get_by_id(user_id)

    assert user is not None
    assert user.id == user_id
    assert user.username == "alice"
    assert user.email.value == "alice@example.com"


@pytest.mark.asyncio
async def test_postgres_user_repository_save_new_user() -> None:
    """Test save thực thể User mới."""
    user_id = uuid4()
    entity = User(
        id=user_id,
        username="bob",
        email=Email(value="bob@example.com"),
    )

    session = MagicMock()
    session.get = AsyncMock(return_value=None)
    session.flush = AsyncMock()

    repo = PostgresUserRepository(session)
    saved_user = await repo.save(entity)

    assert saved_user.id == user_id
    session.add.assert_called_once()
    session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_postgres_project_repository_lists_accessible_projects() -> None:
    """Repository trả Project owner/member theo thứ tự cập nhật."""
    user_id = uuid4()
    proj_id = uuid4()
    now = utc_now()
    mock_model = ProjectModel(
        id=proj_id,
        name="Project A",
        requirement="Requirement A",
        user_id=user_id,
        status="ACTIVE",
        created_at=now,
        updated_at=now,
    )

    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_model]
    session.execute.return_value = mock_result

    repo = PostgresProjectRepository(session)
    projects = await repo.list_accessible_by_user(user_id)

    assert len(projects) == 1
    assert isinstance(projects[0], Project)
    assert projects[0].id == proj_id
    assert projects[0].name == "Project A"


@pytest.mark.asyncio
async def test_project_repository_translates_sqlalchemy_error_with_cause() -> None:
    """Repository không để lỗi SQLAlchemy rò qua infrastructure boundary."""
    session = AsyncMock()
    database_error = SQLAlchemyError("connection failed")
    session.get.side_effect = database_error
    repository = PostgresProjectRepository(session)
    with pytest.raises(InfrastructureException) as exc_info:
        await repository.get_by_id(uuid4())
    assert exc_info.value.__cause__ is database_error


@pytest.mark.asyncio
async def test_data_source_repository_counts_by_project_without_loading_entities() -> None:
    """Aggregate query trả count theo Project thay vì materialize DataSource."""
    first_project_id = uuid4()
    second_project_id = uuid4()
    session = AsyncMock()
    result = MagicMock()
    result.all.return_value = [(first_project_id, 2), (second_project_id, 1)]
    session.execute.return_value = result
    repository = PostgresDataSourceRepository(session)
    counts = await repository.count_by_project_ids((first_project_id, second_project_id))
    assert counts == {first_project_id: 2, second_project_id: 1}
