"""Interface duy nhất của module Requirement."""

from abc import ABC, abstractmethod

from src.application.requirements.input import (
    CreateRequirementInput,
    ListRequirementsInput,
)
from src.application.requirements.output import RequirementOutput


class IRequirementService(ABC):
    """Hợp đồng application cho các use case Requirement."""

    @abstractmethod
    async def create_requirement(self, data: CreateRequirementInput) -> RequirementOutput:
        """Tạo mới một yêu cầu nghiệp vụ thô cho dự án."""
        raise NotImplementedError

    @abstractmethod
    async def list_requirements(
        self, data: ListRequirementsInput
    ) -> list[RequirementOutput]:
        """Liệt kê toàn bộ yêu cầu của một dự án."""
        raise NotImplementedError
