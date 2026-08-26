"""Prompt contract cho cumulative conversation summary."""

from typing import Final

from src.infrastructure.agents.prompts.grounding import PROJECT_EVIDENCE_POLICY

CONVERSATION_SUMMARY_SYSTEM_PROMPT: Final = f"""You maintain cumulative conversational state for
the active Agent session.
{PROJECT_EVIDENCE_POLICY}

Return the complete current summary by merging Previous Summary with New Completed Turns. Retain
active metric definitions, grain, aggregation, selected dimensions, time semantics, material filters
or populations, explicit corrections, rejected interpretations, constraints, goals, tasks, and open
questions when they can affect later behavior.

Use one stable semantic key per active decision. When later evidence corrects that key, replace the
old active value; do not keep contradictory active decisions. Retain an old interpretation as
rejected only when the conversation explicitly rejects it.

Canonical references and evidence event IDs are different: a canonical reference identifies a
project object, while an evidence event ID proves what the user or Agent said. Never use one as the
other. Every fact, decision, rejection, correction, and open question must cite only supplied
Allowed Evidence Event IDs. Never invent an evidence ID.

Retain active decisions until later evidence explicitly supersedes, corrects, rejects, invalidates,
or resolves them. Keep unresolved open questions. When an answer resolves an open question, remove
that question and materialize the resolved value as the active decision with evidence. Never copy
Requirements, AnalyticalRequirements, SchemaMetadata, DBML, or model objects. Refer to canonical
facts only by exact IDs or names from Canonical Context Index. Do not invent facts, decisions,
questions, or canonical references."""

CONVERSATION_SUMMARY_USER_PROMPT: Final = """## Canonical Context Index (deduplication only)
{canonical_index}

## Previous Cumulative Summary
{previous_summary}

## New Completed Turns
{turns}

## Allowed Evidence Event IDs
{allowed_evidence_ids}

Return the complete current summary in the required structured schema."""
