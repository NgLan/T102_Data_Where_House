"""Public contract của Agent Tool registry/executor."""

from abc import ABC, abstractmethod

from src.application.agent_tools.models import (
    AgentToolPreparation,
    AgentToolRequest,
    AgentToolResult,
)


class IAgentToolService(ABC):
    @abstractmethod
    async def prepare(self, data: AgentToolRequest) -> AgentToolPreparation:
        """Resolve revision và config an toàn trước confirmation."""

    @abstractmethod
    async def execute(self, data: AgentToolRequest) -> AgentToolResult:
        """Thực thi đúng một tool trong allowlist."""

    @abstractmethod
    async def read_artifact(self, storage_path: str) -> bytes:
        """Read a previously persisted artifact by its internal path."""
