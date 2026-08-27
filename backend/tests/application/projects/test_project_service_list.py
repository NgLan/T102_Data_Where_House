from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.application.projects.project_service import ProjectService
from src.domain.data_model.entities import DataModel
from src.domain.project.entities import Project


@pytest.mark.asyncio
async def test_list_projects_batches_models_and_computes_outdated_flag() -> None:
    actor_id = uuid4()
    current = Project(
        name="Current", user_id=actor_id,
        analyzed_requirement_revision=2, analyzed_source_revision=3,
    )
    stale = Project(
        name="Stale", user_id=actor_id,
        analyzed_requirement_revision=4, analyzed_source_revision=5,
    )
    missing = Project(name="Missing", user_id=actor_id)
    models = {
        current.id: DataModel(
            project_id=current.id, dbml="Table current { id int [pk] }",
            generated_from_requirement_revision=2, generated_from_source_revision=3,
        ),
        stale.id: DataModel(
            project_id=stale.id, dbml="Table stale { id int [pk] }",
            generated_from_requirement_revision=3, generated_from_source_revision=5,
        ),
    }
    projects = MagicMock()
    projects.list_accessible_by_user = AsyncMock(return_value=[current, stale, missing])
    projects.get_latest_activity_by_project_ids = AsyncMock(return_value={})
    data_sources = MagicMock()
    data_sources.count_by_project_ids = AsyncMock(return_value={})
    data_models = MagicMock()
    data_models.list_by_project_ids = AsyncMock(return_value=models)
    access = MagicMock(actor_id=actor_id)
    service = ProjectService(
        projects, MagicMock(), data_sources, MagicMock(), data_models,
        MagicMock(), MagicMock(), access,
    )

    result = await service.list_projects()

    project_ids = (current.id, stale.id, missing.id)
    data_models.list_by_project_ids.assert_awaited_once_with(project_ids)
    projects.get_latest_activity_by_project_ids.assert_awaited_once_with(project_ids)
    assert [item.is_data_model_outdated for item in result] == [False, True, False]


@pytest.mark.asyncio
async def test_list_projects_sorts_by_latest_activity_descending() -> None:
    actor_id = uuid4()
    p1 = Project(name="Project Alpha", user_id=actor_id, updated_at=datetime(2026, 1, 1, tzinfo=UTC))
    p2 = Project(name="Project Beta", user_id=actor_id, updated_at=datetime(2026, 1, 2, tzinfo=UTC))

    latest_activities = {
        p1.id: datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
        p2.id: datetime(2026, 1, 2, tzinfo=UTC),
    }
    projects = MagicMock()
    projects.list_accessible_by_user = AsyncMock(return_value=[p2, p1])
    projects.get_latest_activity_by_project_ids = AsyncMock(return_value=latest_activities)
    data_sources = MagicMock()
    data_sources.count_by_project_ids = AsyncMock(return_value={})
    data_models = MagicMock()
    data_models.list_by_project_ids = AsyncMock(return_value={})
    access = MagicMock(actor_id=actor_id)
    service = ProjectService(
        projects, MagicMock(), data_sources, MagicMock(), data_models,
        MagicMock(), MagicMock(), access,
    )

    result = await service.list_projects()

    assert [item.name for item in result] == ["Project Alpha", "Project Beta"]
    assert result[0].updated_at == datetime(2026, 8, 28, 12, 0, tzinfo=UTC)
