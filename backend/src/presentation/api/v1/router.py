"""Router tổng hợp toàn bộ endpoint phiên bản v1."""

from fastapi import APIRouter
from src.presentation.api.v1 import data_model_changes, data_models

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(data_models.router)
v1_router.include_router(data_model_changes.router)
