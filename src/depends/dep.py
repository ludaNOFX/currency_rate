from typing import Optional

from core.dto.currency_dto import AmountCurrencyListDTO, CodeCurrencyListDTO
from core.repo.portfolio_repo import Portfolio
from core.interface.portfolio import IPortfolio
from infra.services.currency.currency_service import CurrencyHTTP


def json_keys() -> dict[str, str]:
    """Сюда тоже можно будет потом указывать ключи для DTO но я пока так укажу"""
    return {
        "CharCode": "code",
        "Value": "value",
    }


def currency_http() -> CurrencyHTTP:
    return CurrencyHTTP()


def create_repo_portfolio(
    initial_amounts: AmountCurrencyListDTO,
    currencies: Optional[CodeCurrencyListDTO] = None,  # noqa: UP007
) -> IPortfolio:
    return Portfolio(initial_amounts, currencies)
