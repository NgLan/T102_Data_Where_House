"""Native structured-output schema for semantic Data Model analysis."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from src.application.data_model_analysis.models import EvidenceLevel


class SemanticObservationOutput(BaseModel):
    """Một nhận định semantic kèm reference có thể kiểm chứng."""

    model_config = ConfigDict(extra="forbid")

    explanation: str = Field(min_length=1, max_length=1_000)
    evidence: EvidenceLevel
    table_name: str | None = None
    column_name: str | None = None
    requirement_id: UUID | None = None
    source_id: UUID | None = None


class DataModelAnalysisAgentOutput(BaseModel):
    """Structured output giới hạn cho analysis-agent."""

    model_config = ConfigDict(extra="forbid")

    observations: list[SemanticObservationOutput] = Field(max_length=50)
    uncertainties: list[str] = Field(max_length=30)
