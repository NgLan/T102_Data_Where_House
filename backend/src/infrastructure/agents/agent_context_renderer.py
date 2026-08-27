"""Render immutable workflow context thành JSON dành cho prompt."""

from dataclasses import asdict
from enum import Enum

from src.application.data_warehouse_workflows.input import DataWarehouseDesignInput, RevisionDesignInput
from src.application.requirements.input import (
    DeriveAnalyticalRequirementsInput,
)
from src.common.utils.json import safe_json_dumps
from src.domain.data_source.entities import DataSource
from src.infrastructure.agents.transport_references import TransportReferenceMap


def render_analytical_input(
    data: DeriveAnalyticalRequirementsInput,
    references: TransportReferenceMap,
) -> str:
    """Render Requirements đã rõ semantic mà không dùng source availability."""
    requirements = [
        {
            "requirement_ref": references.reference_for(item.id),
            "title": item.title,
            "description": item.description,
            "requirement_type": _enum_value(item.requirement_type),
            "priority": _enum_value(item.priority),
        }
        for item in data.requirements
    ]
    return _json(requirements)


def render_design_input(
    data: DataWarehouseDesignInput | RevisionDesignInput,
) -> tuple[str, str, str]:
    """Render ba nhóm context bắt buộc của DWDesignAgent."""
    return (
        _json(_design_requirements(data)),
        _json(_analytical_requirements(data)),
        _render_sources(data.data_sources),
    )


def _design_requirements(
    data: DataWarehouseDesignInput | RevisionDesignInput,
) -> list[dict[str, object]]:
    """Chọn các field Requirement cần đưa vào prompt thiết kế."""
    return [
        {
            "id": str(item.id),
            "title": item.title,
            "description": item.description,
            "type": item.type.value,
            "priority": item.priority.value,
        }
        for item in data.requirements
    ]


def _analytical_requirements(
    data: DataWarehouseDesignInput | RevisionDesignInput,
) -> list[dict[str, object]]:
    """Chọn các field Analytical Requirement cần cho thiết kế."""
    return [
        {
            "source_requirement_id": str(item.requirement_id),
            "metric": item.metric,
            "dimension": item.dimension,
            "time_granularity": item.time_granularity,
            "aggregation_method": item.aggregation_method.value if item.aggregation_method else None,
            "grain": item.grain,
        }
        for item in data.analytical_requirements
    ]


def _render_sources(data_sources: tuple[DataSource, ...]) -> str:
    """Render schema thật từ parser mà không gửi absolute file location."""
    payload = [
        {
            "id": str(item.id),
            "name": item.name,
            "type": item.type.value,
            "description": item.description,
            "schema_metadata": asdict(item.schema_metadata) if item.schema_metadata else None,
        }
        for item in data_sources
    ]
    return _json(payload)


def _json(payload: object) -> str:
    """Serialize prompt JSON ổn định và hỗ trợ Enum/UUID."""
    return safe_json_dumps(payload, indent=2)


def _enum_value(value: Enum | str) -> str:
    return str(value.value) if isinstance(value, Enum) else value
