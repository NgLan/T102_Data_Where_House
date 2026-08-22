"""Application service duy nhất cho module Requirement."""

from src.application.common.project_access_policy import ProjectAccessPolicy
from src.application.requirements.i_requirement_service import IRequirementService
from src.application.requirements.input import ListRequirementsInput
from src.application.requirements.output import RequirementOutput
from src.domain.requirement.i_requirement_repository import IRequirementRepository
from typing_extensions import override


class RequirementService(IRequirementService):
    """Điều phối Requirement qua Domain repository và policy dự án."""

    def __init__(
        self,
        requirements: IRequirementRepository,
        access: ProjectAccessPolicy,
    ) -> None:
        self._requirements = requirements
        self._access = access

    @override
    async def list_requirements(
        self,
        data: ListRequirementsInput,
    ) -> list[RequirementOutput]:
        """Liệt kê yêu cầu nếu actor là thành viên dự án."""
        await self._access.require_member(data.project_id)
        requirements = await self._requirements.list_by_project(data.project_id)
        return [RequirementOutput.from_domain(item) for item in requirements]
