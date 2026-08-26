"""Composition root của Project Initialization workflow."""

from typing import Annotated

from fastapi import Depends
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataWarehouseWorkflowService,
)
from src.application.project_initialization import IProjectInitializationService
from src.application.project_initialization.project_initialization_service import (
    ProjectInitializationService,
)
from src.application.requirements.i_requirement_service import IRequirementService
from src.presentation.dependencies.data_warehouse_workflows import (
    get_data_warehouse_workflow,
)
from src.presentation.dependencies.requirements import get_requirement_service


def get_project_initialization_service(
    requirements: Annotated[IRequirementService, Depends(get_requirement_service)],
    data_warehouse: Annotated[
        IDataWarehouseWorkflowService, Depends(get_data_warehouse_workflow)
    ],
) -> IProjectInitializationService:
    """Ghép các application interface thành workflow request-scoped."""
    return ProjectInitializationService(requirements, data_warehouse)


ProjectInitializationServiceDependency = Annotated[
    IProjectInitializationService,
    Depends(get_project_initialization_service),
]
