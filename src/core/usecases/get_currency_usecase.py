import logging
from core.dto.currency_dto import CurrencyDTO
from core.exceptions import CurrencyNotFoundError
from core.interface.portfolio import IPortfolio

logger = logging.getLogger(__name__)


class Usecase:
    def __init__(self, repo: IPortfolio) -> None:
        self._repo = repo

    async def __call__(self, currency: str) -> CurrencyDTO:
        try:
            res = self._repo.get_rate(currency=currency)
        except CurrencyNotFoundError as e:
            logger.warning(f"Currency not found: {currency}")
            raise e  # Пробрасываем специальное исключение
        return res
