import pytest
from core.repo.portfolio_repo import Portfolio
from src.core.dto.currency_dto import (
    AmountCurrencyListDTO,
    CodeCurrencyDTO,
    CodeCurrencyListDTO,
    CurrencyAmountDTO,
    CurrencyDTO,
    CurrencyListDTO,
)


@pytest.fixture(scope="function")
def initial_amounts():
    return AmountCurrencyListDTO(
        items=[
            CurrencyAmountDTO(code="USD", amount=100.0),
            CurrencyAmountDTO(code="EUR", amount=200.0),
            CurrencyAmountDTO(code="RUB", amount=5000.0),
        ]
    )


@pytest.fixture(scope="function")
def initial_currencies():
    return CodeCurrencyListDTO(
        items=[
            CodeCurrencyDTO(code="USD"),
            CodeCurrencyDTO(code="EUR"),
            CodeCurrencyDTO(code="RUB"),
        ]
    )


@pytest.fixture(scope="function")
def exchange_rates():
    return CurrencyListDTO(
        items=[CurrencyDTO(code="USD", value=90.0), CurrencyDTO(code="EUR", value=100.0)]
    )


@pytest.fixture(scope="function")
def portfolio(initial_amounts, initial_currencies):
    return Portfolio(initial_amounts=initial_amounts, currencies=initial_currencies)
