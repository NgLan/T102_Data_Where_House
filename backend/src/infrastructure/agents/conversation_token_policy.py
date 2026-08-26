"""Central token policy và allocation telemetry models."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConversationTokenPolicy:
    """Token window, output reserve và non-binding category targets."""

    total_context_tokens: int
    agent_max_output_tokens: int
    project_context_soft_target: float = 0.45
    summary_soft_target: float = 0.10
    history_soft_target: float = 0.20

    @property
    def output_reserve(self) -> int:
        return max(int(self.total_context_tokens * 0.15), self.agent_max_output_tokens)

    @property
    def soft_target_tokens(self) -> dict[str, int]:
        """Telemetry guardrails; không partition hoặc reject category vượt target."""
        total = self.total_context_tokens
        return {
            "project_context": int(total * self.project_context_soft_target),
            "summary": int(total * self.summary_soft_target),
            "history": int(total * self.history_soft_target),
        }


@dataclass(frozen=True, slots=True)
class BuiltConversationPrompt:
    """Prompt đã fit budget cùng telemetry không chứa raw content."""

    user_prompt: str
    section_tokens: dict[str, int]
    retained_turns: int
    dropped_turns: int
    projection_tier: int
    soft_target_tokens: dict[str, int]
