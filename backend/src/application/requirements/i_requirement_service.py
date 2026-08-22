"""Interface duy nhất của module Requirement."""

from abc import ABC, abstractmethod

from src.application.requirements.input import ListRequirementsInput
from src.application.requirements.output import RequirementOutput


class IRequirementService(ABC):
    """Hợp đồng application cho các use case Requirement."""

    @abstractmethod
    async def list_requirements(
        self, data: ListRequirementsInput
    ) -> list[RequirementOutput]:
        """Liệt kê toàn bộ yêu cầu của một dự án.

        Args:
            data: Project cần đọc yêu cầu.
        Returns:
            Danh sách yêu cầu nghiệp vụ.
        Raises:
            BusinessException: Khi actor không phải thành viên.
            InfrastructureException: Khi persistence thất bại.
        """
        raise NotImplementedError
