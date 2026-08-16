"""Regression tests cho contract giữa Domain và Infrastructure repository."""

from collections.abc import Callable
from inspect import signature
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.domain.analytical_requirement.repository import (
    IAnalyticalRequirementRepository,
)
from src.domain.data_model.repository import (
    IDataModelChangeRepository,
    IDataModelRepository,
)
from src.domain.data_source.repository import IDataSourceRepository
from src.domain.project.repository import IProjectMemberRepository, IProjectRepository
from src.domain.project_session.repository import (
    IProjectSessionRepository,
    ISessionEventRepository,
)
from src.domain.requirement.repository import IRequirementRepository
from src.domain.user.repository import IUserRepository
from src.infrastructure.repositories.postgres_agent_session_repository import (
    PostgresAgentSessionRepository,
)
from src.infrastructure.repositories.postgres_analytical_requirement_repository import (
    PostgresAnalyticalRequirementRepository,
)
from src.infrastructure.repositories.postgres_data_model_change_repository import (
    PostgresDataModelChangeRepository,
)
from src.infrastructure.repositories.postgres_data_model_repository import (
    PostgresDataModelRepository,
)
from src.infrastructure.repositories.postgres_data_source_repository import (
    PostgresDataSourceRepository,
)
from src.infrastructure.repositories.postgres_project_member_repository import (
    PostgresProjectMemberRepository,
)
from src.infrastructure.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)
from src.infrastructure.repositories.postgres_requirement_repository import (
    PostgresRequirementRepository,
)
from src.infrastructure.repositories.postgres_session_event_repository import (
    PostgresSessionEventRepository,
)
from src.infrastructure.repositories.postgres_user_repository import (
    PostgresUserRepository,
)

REPOSITORY_CONTRACTS = (
    (PostgresUserRepository, IUserRepository),
    (PostgresProjectRepository, IProjectRepository),
    (PostgresProjectMemberRepository, IProjectMemberRepository),
    (PostgresRequirementRepository, IRequirementRepository),
    (PostgresAnalyticalRequirementRepository, IAnalyticalRequirementRepository),
    (PostgresDataSourceRepository, IDataSourceRepository),
    (PostgresAgentSessionRepository, IProjectSessionRepository),
    (PostgresSessionEventRepository, ISessionEventRepository),
    (PostgresDataModelRepository, IDataModelRepository),
    (PostgresDataModelChangeRepository, IDataModelChangeRepository),
)


@pytest.mark.parametrize(("implementation", "interface"), REPOSITORY_CONTRACTS)
def test_repository_methods_explicitly_override_interface(implementation: type, interface: type) -> None:
    """Mọi abstract method phải được override với cùng public parameter contract."""
    for method_name in interface.__abstractmethods__:
        method = cast(
            Callable[..., object] | None,
            implementation.__dict__.get(method_name),
        )
        assert method is not None
        assert getattr(method, "__override__", False)
        interface_method = _find_interface_method(interface, method_name)
        assert _parameters(method) == _parameters(interface_method)
        if method_name == "delete":
            assert signature(method).return_annotation is bool


@pytest.mark.asyncio
@pytest.mark.parametrize(("implementation", "_interface"), REPOSITORY_CONTRACTS)
async def test_repository_delete_returns_false_when_entity_is_missing(implementation: type, _interface: type) -> None:
    """Concrete delete phải giữ contract bool khi entity không tồn tại."""
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result
    session.get.return_value = None

    repository = implementation(session)

    assert await repository.delete(entity_id=uuid4()) is False
    session.delete.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(("implementation", "_interface"), REPOSITORY_CONTRACTS)
async def test_repository_delete_returns_true_after_deletion(implementation: type, _interface: type) -> None:
    """Concrete delete phải trả True sau khi xóa và flush thành công."""
    session = AsyncMock()
    result = MagicMock()
    model = MagicMock()
    result.scalar_one_or_none.return_value = model
    session.execute.return_value = result
    session.get.return_value = model

    repository = implementation(session)

    assert await repository.delete(entity_id=uuid4()) is True
    session.delete.assert_awaited_once_with(model)
    session.flush.assert_awaited_once()


def _find_interface_method(interface: type, method_name: str) -> Callable[..., object]:
    """Tìm method khai báo gần nhất trong cây kế thừa interface."""
    for base in interface.__mro__:
        if method_name in base.__dict__:
            return cast(Callable[..., object], base.__dict__[method_name])
    raise AssertionError(f"Missing interface method: {method_name}")


def _parameters(method: Callable[..., object]) -> list[tuple[str, str]]:
    """Lấy tên và loại parameter để kiểm tra keyword-call compatibility."""
    return [(item.name, item.kind.name) for item in signature(method).parameters.values()]
