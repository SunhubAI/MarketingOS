from fastapi import APIRouter

from app.api.routes.bulk_jobs import router as bulk_jobs_router
from app.api.routes.packs import router as packs_router
from app.api.routes.templates import router as templates_router

api_router = APIRouter()
api_router.include_router(templates_router)
api_router.include_router(packs_router)
api_router.include_router(bulk_jobs_router)
