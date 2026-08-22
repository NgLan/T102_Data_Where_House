"""Kiểm thử provisioning actor tại Application boundary."""

from uuid import uuid4

import pytest
from src.application.auth.auth_service import AuthService
from src.application.auth.input import ResolveCurrentActorInput
from src.domain.shared.types import EntityID
from src.domain.user.entities import User
from src.domain.user.i_user_repository import IUserRepository
from typing_extensions import override

from tests.fakes import FakeUnitOfWork


class FakeUserRepository(IUserRepository):
    def __init__(self, users: list[User] | None = None, fail_save: bool = False) -> None:
        self.users = list(users or [])
        self.fail_save = fail_save

    @override
    async def get_by_id(self, entity_id: EntityID) -> User | None:
        return next((user for user in self.users if user.id == entity_id), None)

    @override
    async def get_by_username(self, username: str) -> User | None:
        return next((user for user in self.users if user.username == username), None)

    @override
    async def get_by_email(self, email: str) -> User | None:
        return next((user for user in self.users if user.email.value == email), None)

    @override
    async def save(self, entity: User) -> User:
        if self.fail_save:
            raise RuntimeError("database unavailable")
        self.users.append(entity)
        return entity

    @override
    async def delete(self, entity_id: EntityID) -> bool:
        before = len(self.users)
        self.users = [user for user in self.users if user.id != entity_id]
        return len(self.users) != before


def actor_input(user_id: EntityID) -> ResolveCurrentActorInput:
    return ResolveCurrentActorInput(user_id, "demo-user", "demo@example.com")


@pytest.mark.asyncio
async def test_existing_actor_is_returned_without_write() -> None:
    user = User(id=uuid4(), username="demo-user", email="demo@example.com")
    unit_of_work = FakeUnitOfWork()
    service = AuthService(FakeUserRepository([user]), unit_of_work)

    output = await service.resolve_current_actor(actor_input(user.id))

    assert output.id == user.id
    assert unit_of_work.commit_count == 0


@pytest.mark.asyncio
async def test_missing_actor_is_provisioned_and_committed() -> None:
    unit_of_work = FakeUnitOfWork()
    repository = FakeUserRepository()
    service = AuthService(repository, unit_of_work)

    output = await service.resolve_current_actor(actor_input(uuid4()))

    assert repository.users[0].id == output.id
    assert unit_of_work.commit_count == 1


@pytest.mark.asyncio
async def test_provisioning_failure_rolls_back() -> None:
    unit_of_work = FakeUnitOfWork()
    service = AuthService(FakeUserRepository(fail_save=True), unit_of_work)

    with pytest.raises(RuntimeError):
        await service.resolve_current_actor(actor_input(uuid4()))

    assert unit_of_work.rollback_count == 1
