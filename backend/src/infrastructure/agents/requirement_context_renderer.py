"""Render Requirement clarification context thành prompt an toàn."""

import json
from dataclasses import asdict

from src.application.project_sessions.conversation_context import ConversationTurn
from src.application.requirements.input import ClarifyRequirementsInput


def render_requirement_clarification(data: ClarifyRequirementsInput) -> dict[str, str]:
    """Tách từng nhóm canonical context để không nối document vào raw text."""
    memory = data.conversation
    return {
        "raw_requirement": data.raw_requirement or "(none)",
        "documents": _json([asdict(item) for item in data.documents]),
        "current_requirements": _json([asdict(item) for item in data.current_requirements]),
        "conversation_summary": _json(asdict(memory.summary)) if memory.summary else "(none)",
        "recent_conversation": _render_turns(memory.recent_turns),
        "pending_clarification": _json(asdict(memory.pending)) if memory.pending else "(none)",
        "input_kind": memory.input_kind.value,
        "current_input": memory.current_input,
    }


def _render_turns(turns: tuple[ConversationTurn, ...]) -> str:
    return "\n\n".join(
        f"User: {item.user_content}\nAgent: {item.agent_content}" for item in turns
    ) or "(none)"


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, default=str, separators=(",", ":"))
