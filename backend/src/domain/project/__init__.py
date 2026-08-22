"""Module quản lý Dự án (Project Domain)."""

from src.domain.project.entities import Project, ProjectMember
from src.domain.project.enums import ProjectRole, ProjectStatus
from src.domain.project.i_project_member_repository import IProjectMemberRepository
from src.domain.project.i_project_repository import IProjectRepository
from src.domain.project.value_objects import ProjectDetails

__all__: list[str] = [
    "Project",
    "ProjectMember",
    "ProjectStatus",
    "ProjectRole",
    "IProjectRepository",
    "IProjectMemberRepository",
    "ProjectDetails",
]
