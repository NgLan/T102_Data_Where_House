"""Router tổng hợp cho API phiên bản v1."""

from fastapi import APIRouter
from src.presentation.api.v1.data_models import router as data_models_router
from src.presentation.api.v1.data_sources import router as data_sources_router
from src.presentation.api.v1.projects import router as projects_router
from src.presentation.api.v1.requirements import router as requirements_router


router = APIRouter(prefix="/api/v1")
router.include_router(projects_router)
router.include_router(requirements_router)
router.include_router(data_models_router)
router.include_router(data_sources_router)
