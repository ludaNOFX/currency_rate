from fastapi import APIRouter

from . import health

router = APIRouter(
    prefix="/health",
    tags=["Health v1"],
)

router.include_router(health.router)
