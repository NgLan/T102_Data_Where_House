"""Composition root for the allowlisted Modeling Agent tools."""

from typing import Annotated

from config import get_settings
from fastapi import Depends
from src.application.agent_tools import AgentToolService, IAgentToolService
from src.infrastructure.storage.local_storage import LocalFileStorage
from src.presentation.dependencies.data_model_analysis import DataModelAnalysisDependency
from src.presentation.dependencies.data_models import DataModelServiceDependency
from src.presentation.dependencies.sandbox import SandboxServiceDependency


def get_agent_tool_service(
    models: DataModelServiceDependency,
    analysis: DataModelAnalysisDependency,
    sandbox: SandboxServiceDependency,
) -> IAgentToolService:
    return AgentToolService(
        models,
        analysis,
        sandbox,
        LocalFileStorage(get_settings().upload_dir),
    )


AgentToolDependency = Annotated[
    IAgentToolService,
    Depends(get_agent_tool_service),
]
