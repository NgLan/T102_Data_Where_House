"""Contract tests cho các adapter được chuyển khỏi Domain."""

from collections.abc import Callable
from inspect import signature
from typing import cast

import pytest
from src.application.data_models.i_data_model_service import IDataModelDdlGenerator
from src.application.data_warehouse_workflows.i_data_warehouse_workflow_service import (
    IDataModelValidationEngine,
    IDataWarehouseDesignAgent,
    IRequirementAnalysisAgent,
)
from src.application.sandbox.i_sandbox_service import ISandboxExecutor
from src.infrastructure.agents.data_warehouse_design_agent import DataWarehouseDesignAgent
from src.infrastructure.agents.requirement_analysis_agent import RequirementAnalysisAgent
from src.infrastructure.codegen.pydbml_ddl_generator import PyDbmlDdlGenerator
from src.infrastructure.sandbox.sandbox_executor import PostgresSandboxExecutor
from src.infrastructure.validation.dbml_validation_engine import DbmlValidationEngine

PORT_CONTRACTS = (
    (RequirementAnalysisAgent, IRequirementAnalysisAgent),
    (DataWarehouseDesignAgent, IDataWarehouseDesignAgent),
    (DbmlValidationEngine, IDataModelValidationEngine),
    (PostgresSandboxExecutor, ISandboxExecutor),
    (PyDbmlDdlGenerator, IDataModelDdlGenerator),
)


@pytest.mark.parametrize(("implementation", "interface"), PORT_CONTRACTS)
def test_application_port_adapters_preserve_signature_and_override(
    implementation: type,
    interface: type,
) -> None:
    """Adapter phải override tường minh và giữ nguyên parameter contract của port."""
    methods = interface.__abstractmethods__ or {
        name for name, member in interface.__dict__.items() if callable(member) and not name.startswith("_")
    }
    for method_name in methods:
        method = cast(Callable[..., object], implementation.__dict__[method_name])
        interface_method = cast(Callable[..., object], interface.__dict__[method_name])

        assert getattr(method, "__override__", False)
        assert tuple(signature(method).parameters) == tuple(signature(interface_method).parameters)
