"""Router tổng hợp cho API phiên bản v1."""

from fastapi import APIRouter
from src.presentation.api.v1.data_models import router as data_models_router

router = APIRouter(prefix="/api/v1")
router.include_router(data_models_router)
