"""Application service duy nhất của module Project."""

from src.application.projects.i_project_service import IProjectService


class ProjectService(IProjectService):
    """Điểm hiện thực tập trung cho các use case Project."""
