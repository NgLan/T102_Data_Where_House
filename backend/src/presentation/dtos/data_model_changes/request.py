"""Typed path parameters cho Data Model Change API."""

from typing import Annotated
from uuid import UUID

from fastapi import Path

ChangeIdPath = Annotated[UUID, Path(description="ID đề xuất thay đổi Data Model")]
