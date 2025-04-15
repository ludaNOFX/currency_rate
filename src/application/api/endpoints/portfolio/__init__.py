from fastapi import APIRouter

from . import portfolio

router = APIRouter(
    prefix="/portfolio",
    tags=["Health v1"],
)

router.include_router(portfolio.router)
