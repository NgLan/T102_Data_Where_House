"""Base types dùng chung cho production structured outputs."""

from typing import Annotated, Final

from pydantic import BaseModel, ConfigDict, Field

MIN_CLARIFICATION_OPTIONS: Final[int] = 1
MAX_CLARIFICATION_OPTIONS: Final[int] = 4
MIN_REQUIREMENTS_COUNT: Final[int] = 1
MIN_TEXT_LENGTH: Final[int] = 1

GroundedText = Annotated[str, Field(min_length=MIN_TEXT_LENGTH)]


class AgentOutputBase(BaseModel):
    """Base contract cấm Agent sinh field ngoài operation schema."""

    model_config = ConfigDict(extra="forbid")
