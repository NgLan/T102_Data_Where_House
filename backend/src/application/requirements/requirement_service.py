"""Application service duy nhất cho module Requirement."""

from src.application.common.unit_of_work import IUnitOfWork
from src.application.requirements.i_requirement_service import IRequirementService
from src.application.requirements.input import (
    CreateRequirementInput,
    ListRequirementsInput,
)
from src.application.requirements.output import RequirementOutput
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.domain.project.repository import IProjectRepository
from src.domain.requirement.entities import Requirement
from src.domain.requirement.repository import IRequirementRepository
from src.domain.shared.types import EntityID
from typing_extensions import override


class RequirementService(IRequirementService):
    """Điều phối các use case của Requirement qua domain repository."""

    def __init__(
        self,
        repository: IRequirementRepository,
        project_repository: IProjectRepository,
        unit_of_work: IUnitOfWork,
    ) -> None:
        """Khởi tạo service với repository, kiểm tra dự án và transaction abstraction."""
        self._repository = repository
        self._project_repository = project_repository
        self._unit_of_work = unit_of_work

    @override
    async def create_requirement(self, data: CreateRequirementInput) -> RequirementOutput:
        """Tạo mới một yêu cầu nghiệp vụ thô cho dự án."""
        await self._ensure_project_exists(data.project_id)

        requirement = Requirement(
            project_id=data.project_id,
            title=data.title,
            description=data.description,
            type=data.type,
            priority=data.priority,
        )
        saved = await self._repository.save(requirement)
        await self._unit_of_work.commit()
        return RequirementOutput.from_domain(saved)

    @override
    async def list_requirements(
        self, data: ListRequirementsInput
    ) -> list[RequirementOutput]:
        """Liệt kê toàn bộ yêu cầu của một dự án."""
        await self._ensure_project_exists(data.project_id)

        requirements = await self._repository.list_by_project(data.project_id)
        return [RequirementOutput.from_domain(item) for item in requirements]

    async def _ensure_project_exists(self, project_id: EntityID) -> None:
        """Chuẩn hóa lỗi khi dự án không tồn tại."""
        if await self._project_repository.get_by_id(project_id) is None:
            raise BusinessException(
                code=ErrorCode.PROJECT_NOT_FOUND,
                message="Không tìm thấy dự án được yêu cầu.",
            )
