import logging
from fastapi import APIRouter, Depends, HTTPException, status

from application.depends.provider import get_repo
from core.interface.portfolio import IPortfolio


router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check(repo: IPortfolio = Depends(get_repo)):
    """Проверка работоспособности сервиса и подключения к репозиторию"""
    try:
        # Проверяем базовую операцию чтения
        test_currency = "USD"
        rate = repo.get_rate(test_currency)

        # Проверяем операцию получения списка валют
        currencies = repo.currencies

        return {
            "status": "OK",
            "details": {
                "repository": str(type(repo).__name__),
                "available_currencies": [c.code for c in currencies.items],
                "test_rate": {"currency": test_currency, "rate": rate.value},
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}",
        ) from e
