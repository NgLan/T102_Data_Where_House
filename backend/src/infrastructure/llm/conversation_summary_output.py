"""Structured output schema dành riêng cho conversation compaction."""

from pydantic import BaseModel, ConfigDict, Field


class SummaryOutputBase(BaseModel):
    """Base schema cấm field ngoài structured contract."""

    model_config = ConfigDict(extra="forbid")


class SummaryItemOutput(SummaryOutputBase):
    """Một conversational fact có bounded evidence IDs."""

    statement: str = Field(min_length=1, max_length=1000)
    evidence_event_ids: list[str] = Field(min_length=1, max_length=20)


class SummaryDecisionOutput(SummaryOutputBase):
    """Một active decision có semantic key ổn định."""

    key: str = Field(min_length=1, max_length=200)
    value: str = Field(min_length=1, max_length=1000)
    evidence_event_ids: list[str] = Field(min_length=1, max_length=20)


class ResolvedClarificationOutput(SummaryOutputBase):
    """Một clarification đã giải quyết và evidence pair tương ứng."""

    question: str = Field(min_length=1, max_length=1000)
    answer: str = Field(min_length=1, max_length=1000)
    question_event_id: str
    answer_event_id: str


class ConversationSummaryOutput(SummaryOutputBase):
    """Toàn bộ cumulative state trả về sau một compaction call."""

    current_goal: SummaryItemOutput | None = None
    confirmed_decisions: list[SummaryDecisionOutput] = Field(default_factory=list, max_length=30)
    resolved_clarifications: list[ResolvedClarificationOutput] = Field(default_factory=list, max_length=30)
    important_constraints: list[SummaryItemOutput] = Field(default_factory=list, max_length=30)
    current_task: SummaryItemOutput | None = None
    open_questions: list[SummaryItemOutput] = Field(default_factory=list, max_length=30)
    rejected_assumptions: list[SummaryItemOutput] = Field(default_factory=list, max_length=30)
    canonical_references: list[str] = Field(default_factory=list, max_length=100)
