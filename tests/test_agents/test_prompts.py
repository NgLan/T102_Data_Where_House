"""
Unit tests kiểm tra tính đầy đủ và tuân thủ đặc tả Use Case (UC-01 đến UC-07) của các System Prompts trong src/agents/prompts.py
"""

from backend.src.infrastructure.agents.prompts.prompts import (
    CRITIC_AGENT_SYSTEM_PROMPT,
    CRITIC_AGENT_SYSTEM_PROMPT_VI,
    DESIGN_AGENT_SYSTEM_PROMPT,
    DESIGN_AGENT_SYSTEM_PROMPT_VI,
    ORCHESTRATOR_SYSTEM_PROMPT,
    ORCHESTRATOR_SYSTEM_PROMPT_VI,
)


def test_design_agent_prompt_english_contains_usecase_rules():
    """Kiểm tra Design Agent Prompt tiếng Anh chứa đầy đủ các quy tắc UC-01 đến UC-07."""
    prompt = DESIGN_AGENT_SYSTEM_PROMPT
    assert "Surrogate Key" in prompt
    assert "sandbox_schema." in prompt
    assert "PARTITION BY" in prompt
    assert "NOT ENFORCED" in prompt
    assert "ERR_OUT_OF_SCOPE" in prompt
    assert "postgresql" in prompt.lower()
    assert "snowflake" in prompt.lower()
    assert "bigquery" in prompt.lower()


def test_design_agent_prompt_vietnamese_contains_usecase_rules():
    """Kiểm tra Design Agent Prompt tiếng Việt chứa đầy đủ các quy tắc UC-01 đến UC-07."""
    prompt = DESIGN_AGENT_SYSTEM_PROMPT_VI
    assert "Surrogate Key" in prompt
    assert "sandbox_schema." in prompt
    assert "PARTITION BY" in prompt
    assert "NOT ENFORCED" in prompt
    assert "ERR_OUT_OF_SCOPE" in prompt
    assert "postgresql" in prompt.lower()
    assert "snowflake" in prompt.lower()


def test_critic_agent_prompt_english_contains_antipattern_checklist():
    """Kiểm tra Critic Agent Prompt tiếng Anh chứa danh mục Anti-patterns đầy đủ."""
    prompt = CRITIC_AGENT_SYSTEM_PROMPT
    assert "ERR_OUT_OF_SCOPE" in prompt
    assert "WARN_MISSING_SURROGATE_KEY" in prompt
    assert "WARN_OVER_DENORMALIZATION" in prompt
    assert "CRIT_FAN_TRAP" in prompt
    assert "CRIT_CHASM_TRAP" in prompt
    assert "WARN_BQ_MISSING_PARTITION" in prompt
    assert "WARN_BQ_UNENFORCED_KEY" in prompt
    assert "WARN_ISLAND_FACT" in prompt
    assert "WARN_MISSING_PII_MASKING" in prompt


def test_critic_agent_prompt_vietnamese_contains_antipattern_checklist():
    """Kiểm tra Critic Agent Prompt tiếng Việt chứa danh mục Anti-patterns đầy đủ."""
    prompt = CRITIC_AGENT_SYSTEM_PROMPT_VI
    assert "ERR_OUT_OF_SCOPE" in prompt
    assert "WARN_MISSING_SURROGATE_KEY" in prompt
    assert "WARN_OVER_DENORMALIZATION" in prompt
    assert "CRIT_FAN_TRAP" in prompt
    assert "CRIT_CHASM_TRAP" in prompt
    assert "WARN_BQ_MISSING_PARTITION" in prompt
    assert "WARN_BQ_UNENFORCED_KEY" in prompt
    assert "WARN_ISLAND_FACT" in prompt
    assert "WARN_MISSING_PII_MASKING" in prompt


def test_orchestrator_prompts_contain_boundaries_and_pipeline_steps():
    """Kiểm tra Orchestrator Prompts cả EN và VI đều chứa quy tắc ranh giới và luồng 8 bước."""
    en_prompt = ORCHESTRATOR_SYSTEM_PROMPT
    vi_prompt = ORCHESTRATOR_SYSTEM_PROMPT_VI

    assert "sandbox_schema.*" in en_prompt
    assert "sandbox_schema.*" in vi_prompt
    assert "8 STEPS" in en_prompt or "8-Step" in en_prompt
    assert "8 BƯỚC" in vi_prompt
