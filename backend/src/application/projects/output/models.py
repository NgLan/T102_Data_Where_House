"""Output models độc lập HTTP cho các thao tác Project."""

from dataclasses import dataclass, field
from datetime import datetime

from src.domain.data_source.entities import DataSource
from src.domain.data_source.enums import DataSourceType
from src.domain.data_source.value_objects import SchemaMetadata, TableMetadata
from src.domain.project.entities import Project
from src.domain.project.enums import ProjectStatus
from src.domain.shared.types import EntityID


@dataclass(frozen=True)
class ProjectDataSourceOutput:
    """Thông tin nguồn dữ liệu không làm lộ storage location."""

    id: EntityID
    project_id: EntityID
    name: str
    type: DataSourceType
    description: str | None
    schema_metadata: SchemaMetadata | None

    @property
    def tables(self) -> tuple[TableMetadata, ...]:
        """Cung cấp table metadata cho Presentation mà không sao chép value object."""
        return self.schema_metadata.tables if self.schema_metadata else ()

    @classmethod
    def from_domain(cls, source: DataSource) -> "ProjectDataSourceOutput":
        """Ánh xạ DataSource entity sang application output."""
        return cls(
            id=source.id,
            project_id=source.project_id,
            name=source.name,
            type=source.type,
            description=source.description,
            schema_metadata=source.schema_metadata,
        )


@dataclass(frozen=True)
class ProjectSummaryOutput:
    """Dữ liệu gọn cho danh sách Project."""

    id: EntityID
    name: str
    requirement: str
    user_id: EntityID
    status: ProjectStatus
    domain: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime
    data_source_count: int

    @classmethod
    def from_domain(
        cls,
        project: Project,
        data_source_count: int,
    ) -> "ProjectSummaryOutput":
        """Ánh xạ Project và source count sang summary output."""
        return cls(
            id=project.id,
            name=project.name,
            requirement=project.requirement,
            user_id=project.user_id,
            status=project.status,
            domain=project.domain,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at,
            data_source_count=data_source_count,
        )


@dataclass(frozen=True)
class ProjectOutput(ProjectSummaryOutput):
    """Dữ liệu chi tiết Project và metadata nguồn dữ liệu."""

    data_sources: tuple[ProjectDataSourceOutput, ...] = field(default_factory=tuple)

    @classmethod
    def from_domain(
        cls,
        project: Project,
        sources: tuple[DataSource, ...],
    ) -> "ProjectOutput":
        """Ánh xạ aggregate Project sang application output chi tiết."""
        summary = ProjectSummaryOutput.from_domain(project, len(sources))
        return cls(
            id=summary.id,
            name=summary.name,
            requirement=summary.requirement,
            user_id=summary.user_id,
            status=summary.status,
            domain=summary.domain,
            description=summary.description,
            created_at=summary.created_at,
            updated_at=summary.updated_at,
            data_source_count=summary.data_source_count,
            data_sources=tuple(ProjectDataSourceOutput.from_domain(item) for item in sources),
        )
