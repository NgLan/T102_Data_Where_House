"""Interface duy nhất của module Project."""

from abc import ABC, abstractmethod

from src.application.projects.input import (
    CreateProjectInput,
    ProjectIdInput,
    SaveRawRequirementInput,
    UpdateProjectInput,
)
from src.application.projects.output import (
    ProjectOutput,
    ProjectSummaryOutput,
    RawRequirementOutput,
)
from src.domain.shared.types import EntityID


class IProjectArtifactStore(ABC):
    """Outbound port dọn artifact vật lý của Project."""

    @abstractmethod
    async def delete_project_directory(self, project_id: EntityID) -> None:
        """Xóa toàn bộ artifact vật lý của Project."""
        raise NotImplementedError


class IProjectService(ABC):
    """Hợp đồng application cho toàn bộ use case Project."""

    @abstractmethod
    async def create_project(self, data: CreateProjectInput) -> ProjectOutput:
        """Tạo Project và OWNER membership.

        Args:
            data: Thông tin Project mới.
        Returns:
            Project đã tạo.
        Raises:
            BusinessException: Khi thông tin Project không hợp lệ.
            InfrastructureException: Khi persistence hoặc artifact storage thất bại.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_projects(self) -> tuple[ProjectSummaryOutput, ...]:
        """Liệt kê Project actor hiện tại được truy cập.

        Args:
        Returns:
            Các Project actor là thành viên.
        Raises:
            InfrastructureException: Khi persistence thất bại.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_project(self, data: ProjectIdInput) -> ProjectOutput:
        """Lấy Project nếu actor có membership hợp lệ.

        Args:
            data: Định danh Project.
        Returns:
            Project và các nguồn dữ liệu liên quan.
        Raises:
            BusinessException: Khi Project không tồn tại hoặc actor không phải thành viên.
            InfrastructureException: Khi persistence thất bại.
        """
        raise NotImplementedError

    @abstractmethod
    async def update_project(self, data: UpdateProjectInput) -> ProjectOutput:
        """Cập nhật Project nếu actor là OWNER.

        Args:
            data: Định danh và nội dung thay thế.
        Returns:
            Project sau khi cập nhật.
        Raises:
            BusinessException: Khi Project không hợp lệ hoặc actor không phải OWNER.
            InfrastructureException: Khi persistence thất bại.
        """
        raise NotImplementedError

    @abstractmethod
    async def save_raw_requirement(
        self, data: SaveRawRequirementInput
    ) -> RawRequirementOutput:
        """Lưu Raw Requirement khi expected revision còn hiện hành."""
        raise NotImplementedError

    @abstractmethod
    async def delete_project(self, data: ProjectIdInput) -> None:
        """Xóa Project nếu actor là OWNER.

        Args:
            data: Định danh Project.
        Returns:
            Không có giá trị trả về.
        Raises:
            BusinessException: Khi Project không tồn tại hoặc actor không phải OWNER.
            InfrastructureException: Khi persistence hoặc artifact storage thất bại.
        """
        raise NotImplementedError
