"""Repository contract cho RequirementFile."""

from abc import abstractmethod

from src.domain.requirement_file.entities import RequirementFile
from src.domain.shared.i_base_repository import IBaseRepository
from src.domain.shared.types import EntityID


class IRequirementFileRepository(IBaseRepository[RequirementFile]):
    """Persistence operations của Requirement Documents."""

    @abstractmethod
    async def list_by_project(self, project_id: EntityID) -> list[RequirementFile]:
        """Liệt kê documents theo Project."""

    @abstractmethod
    async def get_by_project_name(
        self, project_id: EntityID, name: str
    ) -> RequirementFile | None:
        """Tìm document theo filename không phân biệt hoa thường."""
