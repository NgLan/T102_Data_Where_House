"""Token-aware prompt builder theo Canonical State > Summary > Raw History."""

import json
from dataclasses import asdict, dataclass

from src.application.data_warehouse_workflows.input import ConversationDesignInput
from src.application.project_sessions.conversation_context import ConversationTurn
from src.common.exceptions.business import BusinessException
from src.common.exceptions.error_codes import ErrorCode
from src.infrastructure.agents.conversation_project_context_projector import (
    ConversationProjectContextProjector,
    ProjectedConversationContext,
)
from src.infrastructure.agents.conversation_token_policy import (
    BuiltConversationPrompt,
    ConversationTokenPolicy,
)
from src.infrastructure.agents.prompts.dw_conversation import DW_CONVERSATION_USER_PROMPT
from src.infrastructure.llm.approximate_token_estimator import ApproximateTokenEstimator


@dataclass(frozen=True, slots=True)
class _ContextFitInput:
    data: ConversationDesignInput
    context: ProjectedConversationContext
    turns: tuple[ConversationTurn, ...]
    system_prompt: str


class ConversationContextBuilder:
    """Chọn projection tier rồi drop nguyên oldest turn trước khi gọi LLM."""

    def __init__(
        self,
        policy: ConversationTokenPolicy,
        estimator: ApproximateTokenEstimator,
    ) -> None:
        self._policy = policy
        self._estimator = estimator
        self._projector = ConversationProjectContextProjector()

    def build(self, data: ConversationDesignInput, system_prompt: str) -> BuiltConversationPrompt:
        turns = data.memory.recent_turns
        for tier in range(3):
            context = self._projector.project(data.revision, data.memory, tier)
            prompt = self._fit_history(
                _ContextFitInput(data, context, turns, system_prompt)
            )
            if prompt:
                return prompt
        raise BusinessException(
            ErrorCode.CONVERSATION_CONTEXT_BUDGET_EXCEEDED,
            "Mandatory conversation context exceeds the configured model window.",
        )

    def _fit_history(
        self,
        fit_input: _ContextFitInput,
    ) -> BuiltConversationPrompt | None:
        retained = fit_input.turns
        while True:
            sections = _prompt_sections(
                fit_input.data, fit_input.context, retained
            )
            sections["system"] = fit_input.system_prompt
            user_prompt = DW_CONVERSATION_USER_PROMPT.format(**sections)
            if self._fits(fit_input.system_prompt, user_prompt):
                counts = (len(retained), len(fit_input.turns), fit_input.context.tier)
                return self._built_prompt(user_prompt, sections, counts)
            if not retained:
                return None
            retained = retained[1:]

    def _fits(self, system_prompt: str, user_prompt: str) -> bool:
        input_budget = self._policy.total_context_tokens - self._policy.output_reserve
        return self._estimator.count(system_prompt, user_prompt) <= input_budget

    def _built_prompt(
        self,
        prompt: str,
        sections: dict[str, str],
        counts: tuple[int, int, int],
    ) -> BuiltConversationPrompt:
        retained, original, tier = counts
        tokens = {key: self._estimator.count(value) for key, value in sections.items()}
        tokens["output_reserve"] = self._policy.output_reserve
        return BuiltConversationPrompt(
            prompt,
            tokens,
            retained,
            original - retained,
            tier,
            self._policy.soft_target_tokens,
        )


def _prompt_sections(
    data: ConversationDesignInput,
    context: ProjectedConversationContext,
    turns: tuple[ConversationTurn, ...],
) -> dict[str, str]:
    memory = data.memory
    return {
        "requirements": context.requirements,
        "analytical_requirements": context.analytical,
        "schema_metadata": context.schemas,
        "current_dbml": context.current_dbml,
        "conversation_summary": _json(asdict(memory.summary)) if memory.summary else "(none)",
        "pending_clarification": _json(asdict(memory.pending)) if memory.pending else "(none)",
        "recent_conversation": _render_turns(turns),
        "input_kind": memory.input_kind.value,
        "instruction": memory.current_input,
    }


def _render_turns(turns: tuple[ConversationTurn, ...]) -> str:
    lines = [f"User: {turn.user_content}\nAgent: {turn.agent_content}" for turn in turns]
    return "\n\n".join(lines) or "(none)"


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, default=str, separators=(",", ":"))
