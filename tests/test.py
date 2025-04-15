import pytest
from core.repo.portfolio_repo import Portfolio
from src.core.dto.currency_dto import (
    AmountCurrencyListDTO,
    CodeCurrencyDTO,
    CodeCurrencyListDTO,
    CurrencyAmountDTO,
    CurrencyDTO,
    CurrencyListDTO,
    SummaryCurrencyDTO,
    TotalCurrencyDTO,
    UpdateCurrencyAmountDTO,
    UpdateCurrencyAmountListDTO,
)
from src.core.exceptions import PortfolioError
from src.core.interface.portfolio import IPortfolio


class TestPortfolio:
    @pytest.fixture
    def initial_amounts(self):
        return AmountCurrencyListDTO(
            items=[
                CurrencyAmountDTO(code="USD", amount=100.0),
                CurrencyAmountDTO(code="EUR", amount=200.0),
                CurrencyAmountDTO(code="RUB", amount=5000.0),
            ]
        )

    @pytest.fixture
    def initial_currencies(self):
        return CodeCurrencyListDTO(
            items=[
                CodeCurrencyDTO(code="USD"),
                CodeCurrencyDTO(code="EUR"),
                CodeCurrencyDTO(code="RUB"),
            ]
        )

    @pytest.fixture
    def exchange_rates(self):
        return CurrencyListDTO(
            items=[
                CurrencyDTO(code="USD", value=90.0),
                CurrencyDTO(code="EUR", value=100.0),
            ]
        )

    @pytest.fixture
    def portfolio(self, initial_amounts, initial_currencies):
        return Portfolio(initial_amounts=initial_amounts, currencies=initial_currencies)

    def test_initialization(self, initial_amounts, initial_currencies):
        portfolio = Portfolio(
            initial_amounts=initial_amounts, currencies=initial_currencies
        )

        # Проверяем, что валюты инициализированы правильно
        assert len(portfolio.currencies.items) == 3
        assert {"USD", "EUR", "RUB"} == {c.code for c in portfolio.currencies.items}

        # Проверяем, что суммы инициализированы правильно
        assert len(portfolio.amount.items) == 3
        assert portfolio.get_amount_one("USD") == 100.0
        assert portfolio.get_amount_one("EUR") == 200.0
        assert portfolio.get_amount_one("RUB") == 5000.0

    def test_default_currencies(self, initial_amounts):
        portfolio = Portfolio(initial_amounts=initial_amounts)
        assert len(portfolio.currencies.items) == 3
        assert {"RUB", "USD", "EUR"} == {c.code for c in portfolio.currencies.items}

    def test_set_exchange_rates(self, portfolio, exchange_rates):
        portfolio.exchange_rates = exchange_rates
        assert portfolio.exchange_rates.items[0].code == "USD"
        assert portfolio.exchange_rates.items[0].value == 90.0
        assert portfolio.exchange_rates.items[1].code == "EUR"
        assert portfolio.exchange_rates.items[1].value == 100.0

    def test_get_rate(self, portfolio, exchange_rates):
        portfolio.exchange_rates = exchange_rates
        assert portfolio.get_rate("USD") == 90.0
        assert portfolio.get_rate("EUR") == 100.0
        with pytest.raises(PortfolioError):
            portfolio.get_rate("GBP")

    def test_set_amount_one(self, portfolio):
        # Устанавливаем новое значение для существующей валюты
        portfolio.set_amount_one(CurrencyAmountDTO(code="USD", amount=150.0))
        assert portfolio.get_amount_one("USD") == 150.0

        # Добавляем новую валюту
        portfolio.set_amount_one(CurrencyAmountDTO(code="GBP", amount=50.0))
        assert portfolio.get_amount_one("GBP") == 50.0

        # Проверяем отрицательное значение
        with pytest.raises(PortfolioError):
            portfolio.set_amount_one(CurrencyAmountDTO(code="USD", amount=-10.0))

    def test_modify_amount_one(self, portfolio):
        # Увеличиваем количество
        portfolio.modify_amount_one(UpdateCurrencyAmountDTO(code="USD", delta=50.0))
        assert portfolio.get_amount_one("USD") == 150.0

        # Уменьшаем количество
        portfolio.modify_amount_one(UpdateCurrencyAmountDTO(code="USD", delta=-30.0))
        assert portfolio.get_amount_one("USD") == 120.0

        # Пытаемся уменьшить ниже нуля
        with pytest.raises(PortfolioError):
            portfolio.modify_amount_one(UpdateCurrencyAmountDTO(code="USD", delta=-200.0))

        # Несуществующая валюта
        with pytest.raises(PortfolioError):
            portfolio.modify_amount_one(UpdateCurrencyAmountDTO(code="GBP", delta=10.0))

    def test_set_multiple_amounts(self, portfolio):
        new_amounts = AmountCurrencyListDTO(
            items=[
                CurrencyAmountDTO(code="USD", amount=300.0),
                CurrencyAmountDTO(code="GBP", amount=400.0),
            ]
        )
        portfolio.set_multiple_amounts(new_amounts)

        assert portfolio.get_amount_one("USD") == 300.0
        assert portfolio.get_amount_one("GBP") == 400.0
        assert portfolio.get_amount_one("EUR") == 200.0  # Должно остаться без изменений

        # Проверяем отрицательные значения
        with pytest.raises(PortfolioError):
            bad_amounts = AmountCurrencyListDTO(
                items=[CurrencyAmountDTO(code="USD", amount=-100.0)]
            )
            portfolio.set_multiple_amounts(bad_amounts)

    def test_modify_multiple_amounts(self, portfolio):
        modifications = UpdateCurrencyAmountListDTO(
            items=[
                UpdateCurrencyAmountDTO(code="USD", delta=50.0),
                UpdateCurrencyAmountDTO(code="EUR", delta=-100.0),
            ]
        )
        portfolio.modify_multiple_amounts(modifications)

        assert portfolio.get_amount_one("USD") == 150.0
        assert portfolio.get_amount_one("EUR") == 100.0

        # Проверяем ошибку при отрицательном результате
        with pytest.raises(PortfolioError):
            bad_modifications = UpdateCurrencyAmountListDTO(
                items=[UpdateCurrencyAmountDTO(code="EUR", delta=-200.0)]
            )
            portfolio.modify_multiple_amounts(bad_modifications)

    def test_get_total(self, portfolio, exchange_rates):
        portfolio.exchange_rates = exchange_rates

        # Проверяем расчет в RUB (по умолчанию)
        total_rub = portfolio.get_total()
        expected_rub = (100.0 * 90.0) + (200.0 * 100.0) + 5000.0
        assert total_rub.total_amount == pytest.approx(expected_rub, 0.01)
        assert total_rub.code == "RUB"

        # Проверяем расчет в USD
        total_usd = portfolio.get_total(in_currency="USD")
        expected_usd = expected_rub / 90.0
        assert total_usd.total_amount == pytest.approx(expected_usd, 0.01)
        assert total_usd.code == "USD"

        # Проверяем ошибку при неизвестной валюте
        with pytest.raises(PortfolioError):
            portfolio.get_total(in_currency="GBP")

    def test_get_portfolio_summary(self, portfolio, exchange_rates):
        portfolio.exchange_rates = exchange_rates
        summary = portfolio.get_portfolio_summary()

        assert isinstance(summary, SummaryCurrencyDTO)
        assert len(summary.amounts.items) == 3
        assert len(summary.rates.items) == 2
        assert summary.total.code == "RUB"

        # Проверяем правильность расчета общей суммы
        expected_total = (100.0 * 90.0) + (200.0 * 100.0) + 5000.0
        assert summary.total.total_amount == pytest.approx(expected_total, 0.01)

    def test_has_changes(self, portfolio, exchange_rates):
        initial_state = {"amounts": dict(portfolio._amount_index), "rates": None}

        # Проверяем без изменений
        assert not portfolio.has_changes(initial_state)

        # Изменяем количество
        portfolio.set_amount_one(CurrencyAmountDTO(code="USD", amount=150.0))
        assert portfolio.has_changes(initial_state)

        # Обновляем состояние
        new_state = {"amounts": dict(portfolio._amount_index), "rates": None}
        assert not portfolio.has_changes(new_state)

        # Изменяем курсы
        portfolio.exchange_rates = exchange_rates
        assert portfolio.has_changes(new_state)

    def test_update_rates(self, portfolio):
        # Проверяем обновление курсов
        new_rates = CurrencyListDTO(
            items=[
                CurrencyDTO(code="USD", value=95.0),
                CurrencyDTO(code="EUR", value=105.0),
            ]
        )
        portfolio.update_rates(new_rates)

        assert portfolio.get_rate("USD") == 95.0
        assert portfolio.get_rate("EUR") == 105.0

        # Проверяем ошибку при отсутствии обязательных валют
        bad_rates = CurrencyListDTO(items=[CurrencyDTO(code="USD", value=95.0)])
        with pytest.raises(PortfolioError):
            portfolio.update_rates(bad_rates)

        # Проверяем ошибку при отрицательном курсе
        bad_rates = CurrencyListDTO(
            items=[
                CurrencyDTO(code="USD", value=-1.0),
                CurrencyDTO(code="EUR", value=105.0),
            ]
        )
        with pytest.raises(PortfolioError):
            portfolio.update_rates(bad_rates)

    def test_negative_amount_validation(self, initial_currencies):
        # Проверяем, что нельзя создать портфель с отрицательными суммами
        bad_amounts = AmountCurrencyListDTO(
            items=[
                CurrencyAmountDTO(code="USD", amount=-100.0),
                CurrencyAmountDTO(code="EUR", amount=200.0),
            ]
        )

        with pytest.raises(PortfolioError):
            Portfolio(initial_amounts=bad_amounts, currencies=initial_currencies)
