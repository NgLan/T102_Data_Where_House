"""Đọc canonical project index tối thiểu dành riêng cho summary deduplication."""

from dataclasses import dataclass

from src.domain.analytical_requirement.i_analytical_requirement_repository import (
    IAnalyticalRequirementRepository,
)
from src.domain.data_model.i_data_model_repository import IDataModelRepository
from src.domain.data_source.i_data_source_repository import IDataSourceRepository
from src.domain.requirement.i_requirement_repository import IRequirementRepository
from src.domain.shared.types import EntityID


@dataclass(frozen=True, slots=True)
class CanonicalIndexDependencies:
    """Repository bundle chỉ dùng để đọc canonical reference index."""

    requirements: IRequirementRepository
    analytical: IAnalyticalRequirementRepository
    data_sources: IDataSourceRepository
    models: IDataModelRepository


class ConversationCanonicalIndexReader:
    """Chỉ đọc ID/name; không đưa canonical payload vào conversation summary."""

    def __init__(self, dependencies: CanonicalIndexDependencies) -> None:
        self._dependencies = dependencies

    async def read(self, project_id: EntityID) -> tuple[str, ...]:
        dependencies = self._dependencies
        requirements = await dependencies.requirements.list_by_project(project_id)
        analytical = await dependencies.analytical.list_by_project(project_id)
        sources = await dependencies.data_sources.list_by_project(project_id)
        model = await dependencies.models.get_by_project_id(project_id)
        entries = [f"requirement:{item.id}:{item.title}" for item in requirements]
        entries.extend(f"analytical_requirement:{item.id}" for item in analytical)
        entries.extend(f"data_source:{item.id}:{item.name}" for item in sources)
        if model:
            entries.append(f"data_model:{model.id}")
        return tuple(entries)
