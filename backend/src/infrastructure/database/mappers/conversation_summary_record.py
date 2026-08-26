"""Pydantic persistence records for structured conversation summaries."""

from pydantic import BaseModel, ConfigDict, Field


class SummaryRecordBase(BaseModel):
    """Base JSONB record không chấp nhận field lạ."""

    model_config = ConfigDict(extra="forbid")


class SummaryItemRecord(SummaryRecordBase):
    """Persistence record cho conversational fact."""

    statement: str
    evidence_event_ids: list[str] = Field(default_factory=list)


class SummaryDecisionRecord(SummaryRecordBase):
    """Persistence record cho active decision."""

    key: str
    value: str
    evidence_event_ids: list[str] = Field(default_factory=list)


class ResolvedClarificationRecord(SummaryRecordBase):
    """Persistence record cho clarification evidence pair."""

    question: str
    answer: str
    question_event_id: str
    answer_event_id: str


class ConversationSummaryRecord(SummaryRecordBase):
    """Validated JSONB representation của cumulative summary."""

    current_goal: SummaryItemRecord | None = None
    confirmed_decisions: list[SummaryDecisionRecord] = Field(default_factory=list)
    resolved_clarifications: list[ResolvedClarificationRecord] = Field(default_factory=list)
    important_constraints: list[SummaryItemRecord] = Field(default_factory=list)
    current_task: SummaryItemRecord | None = None
    open_questions: list[SummaryItemRecord] = Field(default_factory=list)
    rejected_assumptions: list[SummaryItemRecord] = Field(default_factory=list)
    canonical_references: list[str] = Field(default_factory=list)
