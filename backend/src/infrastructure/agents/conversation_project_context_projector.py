"""Operation-aware projection cho canonical context của DW conversation."""

import json
from dataclasses import asdict, dataclass

from lark_dbml import dumps, loads
from lark_dbml.lark_dbml_standalone import UnexpectedInput
from src.application.data_warehouse_workflows.input import RevisionDesignInput
from src.application.project_sessions.conversation_context import ConversationMemory
from src.domain.data_source.entities import DataSource
from src.domain.data_source.value_objects import SchemaMetadata


@dataclass(frozen=True, slots=True)
class ProjectedConversationContext:
    """Các canonical section đã project, giữ riêng để đo token và telemetry."""

    requirements: str
    analytical: str
    schemas: str
    current_dbml: str
    tier: int


class ConversationProjectContextProjector:
    """Bỏ profile/sample payload trước khi context allocator đánh giá budget."""

    def project(
        self,
        revision: RevisionDesignInput,
        memory: ConversationMemory,
        tier: int,
    ) -> ProjectedConversationContext:
        references = _conversation_references(memory)
        return ProjectedConversationContext(
            _json(_requirements(revision)),
            _json(_analytical(revision)),
            _json([_source(item, references, tier) for item in revision.data_sources]),
            _normalized_dbml(revision.current_dbml),
            tier,
        )


def _requirements(revision: RevisionDesignInput) -> list[dict[str, object]]:
    return [
        {
            "id": str(item.id),
            "title": item.title,
            "description": item.description,
            "type": item.type.value,
            "priority": item.priority.value,
        }
        for item in revision.requirements
    ]


def _analytical(revision: RevisionDesignInput) -> list[dict[str, object]]:
    return [
        {
            "id": str(item.id),
            "source_requirement_id": str(item.requirement_id),
            "metric": item.metric,
            "dimension": item.dimension,
            "time_granularity": item.time_granularity,
            "aggregation_method": item.aggregation_method.value if item.aggregation_method else None,
            "grain": item.grain,
        }
        for item in revision.analytical_requirements
    ]


def _source(source: DataSource, references: str, tier: int) -> dict[str, object]:
    schema = source.schema_metadata
    detailed = tier == 0 or (tier == 1 and _is_referenced(source, references))
    return {
        "id": str(source.id),
        "name": source.name,
        "type": source.type.value,
        "description": source.description if detailed else None,
        "tables": _tables(schema, detailed),
        "relationships": _relationships(schema),
    }


def _tables(schema: SchemaMetadata | None, detailed: bool) -> list[dict[str, object]]:
    if schema is None:
        return []
    return [
        {
            "name": table.name,
            "columns": [_column(column, detailed) for column in table.columns],
        }
        for table in schema.tables
    ]


def _relationships(schema: SchemaMetadata | None) -> list[dict[str, object]]:
    if schema is None:
        return []
    return [
        {
            "from_column": item.from_column,
            "to_column": item.to_column,
            "type": item.type.value,
        }
        for item in schema.relationships
    ]


def _column(column: object, detailed: bool) -> dict[str, object]:
    payload = {
        "name": getattr(column, "name"),
        "data_type": getattr(column, "data_type").value,
        "primary_key": getattr(column, "primary_key"),
        "nullable": getattr(column, "nullable"),
        "constraints": [asdict(item) for item in getattr(column, "constraints")],
        "is_key_candidate": getattr(column, "is_key_candidate"),
    }
    if detailed:
        payload["description"] = getattr(column, "description")
    return payload


def _conversation_references(memory: ConversationMemory) -> str:
    values = [memory.current_input]
    values.extend(value for turn in memory.recent_turns for value in (turn.user_content, turn.agent_content))
    if memory.pending:
        values.extend((memory.pending.question, memory.pending.original_intent or ""))
    if memory.summary:
        values.extend(memory.summary.canonical_references)
    return "\n".join(values).casefold()


def _is_referenced(source: DataSource, references: str) -> bool:
    candidates = {source.name.casefold(), str(source.id).casefold()}
    return any(candidate in references for candidate in candidates)


def _normalized_dbml(dbml: str) -> str:
    """Parser/serializer normalization giữ toàn bộ table và relationship semantics."""
    try:
        return dumps(loads(dbml))
    except (TypeError, ValueError, UnexpectedInput):
        return dbml


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)
