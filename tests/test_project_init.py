"""Unit test cho project UUID và Data Model snapshot đầu workflow."""

import pytest
from src.application.projects.input import CreateProjectInput
from src.application.projects.project_service import ProjectService


class InMemoryRepository:
    def __init__(self) -> None:
        self.entities = []

    async def save(self, entity):
        self.entities.append(entity)
        return entity


class InMemoryUserRepository(InMemoryRepository):
    async def get_by_username(self, username: str):
        return next(
            (entity for entity in self.entities if entity.username == username),
            None,
        )


class MockUnitOfWork:
    def __init__(self) -> None:
        self.committed = False

    async def commit(self) -> None:
        self.committed = True


async def _unused(*_args, **_kwargs):
    return None


def attach_unused_repository_methods(repository: InMemoryRepository) -> None:
    repository.get_by_id = _unused
    repository.delete = _unused
    repository.list_by_user = _unused
    repository.get_by_project_id = _unused
    repository.update_if_revision_matches = _unused


@pytest.mark.asyncio
async def test_project_init_creates_uuid_and_initial_data_model() -> None:
    projects = InMemoryRepository()
    data_models = InMemoryRepository()
    users = InMemoryUserRepository()
    for repository in (projects, data_models, users):
        attach_unused_repository_methods(repository)
    unit_of_work = MockUnitOfWork()
    service = ProjectService(projects, data_models, users, unit_of_work)

    output = await service.create_project(
        CreateProjectInput(
            domain="ride",
            target_dialect="postgresql",
            business_description="Phân tích chuyến đi",
            is_masking_enabled=True,
        )
    )
    assert output.project_id == projects.entities[0].id
    assert data_models.entities[0].project_id == output.project_id
    assert unit_of_work.committed is True
