import logging
from core.dto.currency_dto import AmountCurrencyListDTO
from core.exceptions import PortfolioError
from core.interface.portfolio import IPortfolio

logger = logging.getLogger(__name__)


class Usecase:
    def __init__(self, repo: IPortfolio) -> None:
        self._repo = repo

    async def __call__(self, dto: AmountCurrencyListDTO) -> AmountCurrencyListDTO:
        try:
            res = self._repo.set_multiple_amounts(amounts=dto)
        except PortfolioError as e:
            logger.exception(f"Error: {dto.to_dict()}")
            raise e  # Пробрасываем специальное исключение
        return res
