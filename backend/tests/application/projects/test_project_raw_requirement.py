"""Raw Requirement save revision contracts."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.projects.input import SaveRawRequirementInput
from src.application.projects.project_service import ProjectService
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project.entities import Project

from tests.fakes import (
    FakeDataModelRepository,
    FakeDataSourceRepository,
    FakeProjectMemberRepository,
    FakeProjectRepository,
    FakeRequirementRepository,
    FakeUnitOfWork,
)


def _service(project: Project) -> ProjectService:
    projects = FakeProjectRepository([project])
    members = FakeProjectMemberRepository([])
    return ProjectService(
        projects,
        members,
        FakeDataSourceRepository([]),
        FakeRequirementRepository([]),
        FakeDataModelRepository([]),
        MagicMock(),
        FakeUnitOfWork(),
        ProjectAccessPolicy(projects, members, project.user_id),
    )


@pytest.mark.asyncio
async def test_same_normalized_raw_requirement_does_not_increment_revision() -> None:
    project = Project(name="Revenue", requirement="Line one\n  Line two", user_id=uuid4())

    output = await _service(project).save_raw_requirement(
        SaveRawRequirementInput(project.id, "\r\nLine one\r\n  Line two\r\n", 1)
    )

    assert output.requirement == "Line one\n  Line two"
    assert output.requirement_revision == 1


@pytest.mark.asyncio
async def test_changed_raw_requirement_increments_once_and_preserves_markdown() -> None:
    project = Project(name="Revenue", requirement="Original requirement", user_id=uuid4())
    changed = "# Revenue\r\n\r\n-  Keep  spacing"

    output = await _service(project).save_raw_requirement(
        SaveRawRequirementInput(project.id, changed, 1)
    )

    assert output.requirement == "# Revenue\n\n-  Keep  spacing"
    assert output.requirement_revision == 2


@pytest.mark.asyncio
async def test_raw_requirement_rejects_stale_expected_revision() -> None:
    project = Project(name="Revenue", requirement="Original requirement", user_id=uuid4())

    with pytest.raises(BusinessException) as raised:
        await _service(project).save_raw_requirement(
            SaveRawRequirementInput(project.id, "Changed requirement", 0)
        )

    assert raised.value.code is ErrorCode.REQUIREMENT_REVISION_CONFLICT
