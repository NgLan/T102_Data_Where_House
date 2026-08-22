"""Request schemas và parameter constraints cho API Requirement."""

from typing import Annotated
from uuid import UUID

from fastapi import Path

ProjectIdPath = Annotated[UUID, Path(description="ID dự án chứa yêu cầu")]
