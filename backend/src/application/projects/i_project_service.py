"""Interface duy nhất của module Project."""

from abc import ABC, abstractmethod

from src.application.projects.input import (
    CreateProjectInput,
    ListProjectsInput,
    ProjectIdInput,
    UpdateProjectInput,
)
from src.application.projects.output import ProjectOutput, ProjectSummaryOutput


class IProjectService(ABC):
    """Hợp đồng application cho toàn bộ use case Project."""

    @abstractmethod
    async def create_project(self, data: CreateProjectInput) -> ProjectOutput:
        """Tạo Project và OWNER membership."""
        raise NotImplementedError

    @abstractmethod
    async def list_projects(
        self,
        data: ListProjectsInput,
    ) -> tuple[ProjectSummaryOutput, ...]:
        """Liệt kê Project actor hiện tại được truy cập."""
        raise NotImplementedError

    @abstractmethod
    async def get_project(self, data: ProjectIdInput) -> ProjectOutput:
        """Lấy Project nếu actor có membership hợp lệ."""
        raise NotImplementedError

    @abstractmethod
    async def update_project(self, data: UpdateProjectInput) -> ProjectOutput:
        """Cập nhật Project nếu actor là OWNER."""
        raise NotImplementedError

    @abstractmethod
    async def delete_project(self, data: ProjectIdInput) -> None:
        """Xóa Project nếu actor là OWNER."""
        raise NotImplementedError
