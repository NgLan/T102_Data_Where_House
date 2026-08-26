"""Application interface duy nhất của Project Initialization."""

from abc import ABC, abstractmethod

from src.application.project_initialization.models import (
    ProjectInitializationInput,
    ProjectInitializationOutput,
)


class IProjectInitializationService(ABC):
    """Điều phối Requirement, Source analysis và Data Model generation."""

    @abstractmethod
    async def run(
        self, data: ProjectInitializationInput
    ) -> ProjectInitializationOutput:
        """Chạy đến khi cần clarification hoặc DBML đã sẵn sàng."""
        raise NotImplementedError
