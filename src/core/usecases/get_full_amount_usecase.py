import logging
from core.dto.currency_dto import SummaryCurrencyDTO
from core.exceptions import PortfolioError
from core.interface.portfolio import IPortfolio

logger = logging.getLogger(__name__)


class Usecase:
    def __init__(self, repo: IPortfolio) -> None:
        self._repo = repo

    async def __call__(self) -> SummaryCurrencyDTO:
        try:
            res = self._repo.get_portfolio_summary()
        except PortfolioError as e:
            logger.exception("Ошибка Usecase")
            raise e  # Пробрасываем специальное исключение
        return res
