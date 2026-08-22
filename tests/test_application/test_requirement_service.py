"""Kiểm thử chỉnh sửa Requirement từ màn Project Init."""

from uuid import uuid4

import pytest
from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.requirements.input import UpdateRequirementInput
from src.application.requirements.requirement_service import RequirementService
from src.domain.project.entities import Project
from src.domain.requirement.entities import Requirement
from src.domain.requirement.enums import RequirementPriority, RequirementType

from tests.fakes import (
    FakeProjectMemberRepository,
    FakeProjectRepository,
    FakeRequirementRepository,
    FakeUnitOfWork,
)


@pytest.mark.asyncio
async def test_owner_updates_structured_requirement() -> None:
    """OWNER có thể sửa nội dung, type và priority của Requirement."""
    owner_id = uuid4()
    project = Project(name="Sales project", requirement=None, user_id=owner_id)
    requirement = Requirement(
        project_id=project.id,
        title="Doanh thu",
        description="Theo dõi doanh thu.",
    )
    repository = FakeRequirementRepository([requirement])
    unit_of_work = FakeUnitOfWork()
    projects = FakeProjectRepository([project])
    service = RequirementService(
        repository,
        unit_of_work,
        ProjectAccessPolicy(
            projects,
            FakeProjectMemberRepository([]),
            owner_id,
        ),
        projects,
    )

    output = await service.update_requirement(
        UpdateRequirementInput(
            project.id,
            requirement.id,
            "Doanh thu theo tháng",
            "Tổng hợp doanh thu theo từng tháng.",
            RequirementType.ANALYTICAL,
            RequirementPriority.HIGH,
        )
    )

    assert (output.type, output.priority) == (
        RequirementType.ANALYTICAL,
        RequirementPriority.HIGH,
    )
    assert unit_of_work.commit_count == 1
    assert project.requirement_revision == 1
