"""Upload chỉ validate nhẹ, lưu source pending và không có profiler/LLM dependency."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.application.data_sources.data_source_service import DataSourceService
from src.application.data_sources.input import UploadDataSourcesInput, UploadFileInput
from src.domain.data_source.enums import DataSourceType
from src.domain.project.entities import Project


@pytest.mark.asyncio
async def test_upload_returns_pending_without_profiling() -> None:
    project = Project(name="Demo", user_id=uuid4())
    sources, files, inspector = MagicMock(), MagicMock(), MagicMock()
    sources.list_by_project = AsyncMock(return_value=[])
    sources.save = AsyncMock(side_effect=lambda source: source)
    files.save_file = AsyncMock(return_value="stored/orders.csv")
    projects, access = MagicMock(), MagicMock()
    projects.save = AsyncMock()
    access.require_owner = AsyncMock(return_value=project)
    unit_of_work = MagicMock()
    unit_of_work.__aenter__ = AsyncMock(return_value=unit_of_work)
    unit_of_work.__aexit__ = AsyncMock(return_value=None)
    unit_of_work.commit = AsyncMock()
    inspector.source_type.return_value = DataSourceType.CSV
    service = DataSourceService(sources, files, inspector, unit_of_work, access, projects)

    result = await service.upload_data_sources(
        UploadDataSourcesInput(project.id, (UploadFileInput("orders.csv", b"id\n1"),))
    )

    inspector.validate.assert_called_once_with(b"id\n1", "orders.csv")
    assert result.total_files_uploaded == 1
    assert result.data_sources[0].analysis_status.value == "PENDING"
