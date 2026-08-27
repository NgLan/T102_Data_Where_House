"""Regression contracts cho grounding và decision gate của production prompts."""

from src.infrastructure.agents import conversation_output_invoker
from src.infrastructure.agents.prompts import requirement
from src.infrastructure.agents.prompts.conversation_summary import (
    CONVERSATION_SUMMARY_SYSTEM_PROMPT,
)
from src.infrastructure.agents.prompts.dw_conversation import (
    DW_CONVERSATION_SYSTEM_PROMPT,
)
from src.infrastructure.agents.prompts.dw_design import DW_DESIGN_SYSTEM_PROMPT
from src.infrastructure.agents.prompts.dw_revise import DW_REVISE_SYSTEM_PROMPT
from src.infrastructure.agents.prompts.grounding import PROJECT_EVIDENCE_POLICY
from src.infrastructure.agents.prompts.requirement import (
    ANALYTICAL_SYSTEM_PROMPT,
    REQUIREMENT_CLARIFICATION_SYSTEM_PROMPT,
)
from src.infrastructure.llm.column_type_classifier import SYSTEM_PROMPT

SYSTEM_PROMPTS = (
    REQUIREMENT_CLARIFICATION_SYSTEM_PROMPT,
    ANALYTICAL_SYSTEM_PROMPT,
    DW_DESIGN_SYSTEM_PROMPT,
    DW_REVISE_SYSTEM_PROMPT,
    DW_CONVERSATION_SYSTEM_PROMPT,
    CONVERSATION_SUMMARY_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
)


def test_every_production_system_prompt_uses_shared_grounding_policy() -> None:
    assert all(PROJECT_EVIDENCE_POLICY in prompt for prompt in SYSTEM_PROMPTS)


def test_requirement_prompt_uses_analytical_readiness_gate() -> None:
    prompt = REQUIREMENT_CLARIFICATION_SYSTEM_PROMPT
    assert "Understandable wording is not enough for READY" in prompt
    assert "COUNT versus COUNT_DISTINCT" in prompt
    assert "optional drill-downs" in prompt
    assert "exactly one highest-impact question" in prompt
    assert "CLARIFICATION_ANSWER" in prompt
    assert "It does not mean source data is sufficient" in prompt


def test_unused_raw_requirement_prompt_contract_is_removed() -> None:
    assert not hasattr(requirement, "RAW_REQUIREMENT_SYSTEM_PROMPT")
    assert not hasattr(requirement, "RAW_REQUIREMENT_USER_PROMPT")


def test_analytical_prompt_forbids_completing_unsupported_semantics() -> None:
    prompt = ANALYTICAL_SYSTEM_PROMPT
    assert "jointly supported" in prompt
    assert "Never silently omit" in prompt
    assert "NEEDS_REQUIREMENT_CLARIFICATION" in prompt
    assert "NOT_ANALYTICAL" in prompt
    assert "Use null" in prompt


def test_dw_prompts_preserve_scope_and_validation_retry_evidence() -> None:
    assert "working draft" in DW_DESIGN_SYSTEM_PROMPT
    assert "unrelated schema expansion" in DW_DESIGN_SYSTEM_PROMPT
    assert "Apply the user-requested change narrowly" in DW_REVISE_SYSTEM_PROMPT
    assert "do not redesign unrelated areas" in DW_REVISE_SYSTEM_PROMPT
    assert "samples, and statistics do not establish" in DW_DESIGN_SYSTEM_PROMPT


def test_conversation_prompt_has_strict_branch_gate() -> None:
    prompt = DW_CONVERSATION_SYSTEM_PROMPT
    assert "Choose clarification" in prompt
    assert "Choose proposal only" in prompt
    assert "Choose no_change only" in prompt
    assert "do not record it as a standalone fact" in prompt
    assert "primarily" in prompt
    assert "fallback guardrail" in prompt


def test_repair_prompt_cannot_change_semantic_decision() -> None:
    prompt = conversation_output_invoker.OUTPUT_REPAIR_INSTRUCTION
    assert "Correct only the structured shape" in prompt
    assert "preserve the original grounded decision" in prompt


def test_summary_and_classifier_prompts_keep_evidence_bounded() -> None:
    assert "contradictory active decisions" in CONVERSATION_SUMMARY_SYSTEM_PROMPT
    assert "Allowed Evidence Event IDs" in CONVERSATION_SUMMARY_SYSTEM_PROMPT
    assert "Canonical references and evidence event IDs are different" in (CONVERSATION_SUMMARY_SYSTEM_PROMPT)
    assert "exactly one result" in SYSTEM_PROMPT
    assert "not business definitions" in SYSTEM_PROMPT
