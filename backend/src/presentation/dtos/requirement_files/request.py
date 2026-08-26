"""Path constraints cho Requirement File API."""

from typing import Annotated
from uuid import UUID

from fastapi import Path

ProjectIdPath = Annotated[UUID, Path(description="ID Project")]
RequirementFileIdPath = Annotated[UUID, Path(description="ID Requirement Document")]
