"""Render Requirement clarification context thành prompt an toàn."""

from dataclasses import asdict
from enum import Enum

from src.application.project_sessions.conversation_context import ConversationTurn
from src.application.requirements.input import ClarifyRequirementsInput, RequirementContext
from src.common.utils.json import safe_json_dumps
from src.infrastructure.agents.transport_references import TransportReferenceMap


def render_requirement_clarification(
    data: ClarifyRequirementsInput,
    references: TransportReferenceMap,
) -> dict[str, str]:
    """Tách từng nhóm canonical context để không nối document vào raw text."""
    memory = data.conversation
    return {
        "raw_requirement": data.raw_requirement or "(none)",
        "documents": _json([asdict(item) for item in data.documents]),
        "current_requirements": _current_requirements(data.current_requirements, references),
        "conversation_summary": _json(asdict(memory.summary)) if memory.summary else "(none)",
        "recent_conversation": _render_turns(memory.recent_turns),
        "pending_clarification": _json(asdict(memory.pending)) if memory.pending else "(none)",
        "input_kind": memory.input_kind.value,
        "current_input": memory.current_input,
    }


def _current_requirements(
    items: tuple[RequirementContext, ...],
    references: TransportReferenceMap,
) -> str:
    records = [
        {
            "requirement_ref": references.reference_for(item.id),
            "title": item.title,
            "description": item.description,
            "requirement_type": _enum_value(item.requirement_type),
            "priority": _enum_value(item.priority),
        }
        for item in items
    ]
    return _json(records)


def _render_turns(turns: tuple[ConversationTurn, ...]) -> str:
    return "\n\n".join(f"User: {item.user_content}\nAgent: {item.agent_content}" for item in turns) or "(none)"


def _json(value: object) -> str:
    return safe_json_dumps(value)


def _enum_value(value: Enum | str) -> str:
    return str(value.value) if isinstance(value, Enum) else value
