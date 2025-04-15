from collections.abc import Mapping
import logging
from typing import TypeVar, TypedDict, Any, cast, Optional
from collections.abc import Callable

from core.dto.currency_dto import (
    AmountCurrencyListDTO,
    CodeCurrencyListDTO,
    CurrencyAmountDTO,
    CurrencyDTO,
    CurrencyListDTO,
    SummaryCurrencyDTO,
    TotalCurrencyDTO,
    UpdateCurrencyAmountDTO,
    UpdateCurrencyAmountListDTO,
)
from core.entity.currency_item import (
    AmountData,
    CurrencyAmountItem,
    CurrencyData,
    CurrencyItem,
    CurrencyValueItem,
    ExchangeRateData,
)
from core.exceptions import CurrencyNotFoundError, PortfolioError
from core.interface.portfolio import IPortfolio


T = TypeVar("T", bound=TypedDict)
K = TypeVar("K")
V = TypeVar("V")


logger = logging.getLogger(__name__)


class Portfolio(IPortfolio):
    _default_currencies = {"items": [{"code": "RUB"}, {"code": "USD"}, {"code": "EUR"}]}

    def __init__(
        self,
        initial_amounts: AmountCurrencyListDTO,
        currencies: Optional[CodeCurrencyListDTO] = None,  # noqa: UP007
    ) -> None:
        """
        :param initial_amounts: пример DTO -> AmountCurrencyListDTO(items=[CurrencyAmountDTO(code='USD', amount=84.004), CurrencyAmountDTO(code='EUR', amount=96.2163)]) - количество каждой валюты

        :param currencies: пример DTO -> CodeCurrencyListDTO(items=[BaseCurrencyDTO(code='USD'), BaseCurrencyDTO(code='EUR')]) - коды валют
        """  # noqa: E501
        for item in initial_amounts.items:
            if item.amount < 0:
                raise PortfolioError(
                    f"Невозможно установить отрицательное значение для {item.code}"
                )
        self._currencies: CurrencyData = self._convert_to_typed_dict(
            data=currencies.to_dict() if currencies else self._default_currencies,
            container_type=CurrencyData,
            item_type=CurrencyItem,
            required_keys=["code"],
        )

        self._amount: AmountData = self._convert_to_typed_dict(
            data=initial_amounts.to_dict(),
            container_type=AmountData,
            item_type=CurrencyAmountItem,
            required_keys=["code", "amount"],
        )
        self._amount_index: dict[str, float] = self._build_index(
            items=[dict(item) for item in self._amount["items"]],
            key_field="code",
            value_field="amount",
            value_converter=float,
        )
        self._exchange_rates: Optional[ExchangeRateData] = None  # noqa: UP007
        self._rates_index: Optional[dict[str, float]] = None  # noqa: UP007

    @staticmethod
    def _convert_to_typed_dict(
        data: dict[str, Any],
        container_type: type[T],
        item_type: type[Any],
        required_keys: list[str],
    ) -> T:
        """
        Конвертируем в Сущнссти которые используются в Portfolio
        """
        items = []
        for raw_item in data["items"]:
            if not all(key in raw_item for key in required_keys):
                raise PortfolioError(f"Item missing required keys: {required_keys}")

            item_kwargs = {key: raw_item[key] for key in required_keys}
            items.append(item_type(**item_kwargs))

        return cast(container_type, {"items": items})

    @staticmethod
    def _build_index(
        items: list[Mapping[str, Any]],
        key_field: str,
        value_field: str,
        value_converter: Optional[Callable] = None,  # noqa: UP007
    ) -> dict[K, V]:  # type: ignore
        """
        Универсальный метод создания индекса

        :param items: Список элементов
        :param key_field: Поле, используемое как ключ
        :param value_field: Поле, используемое как значение
        :param value_converter: Функция для преобразования значения (опционально)
        :return: Словарь с индексом
        """
        index: dict[K, V] = {}
        for item in items:
            key = item[key_field]
            value = item[value_field]
            if value_converter:
                value = value_converter(value)
            index[key] = value
        return index

    @property
    def currencies(self) -> CodeCurrencyListDTO:
        """Получить список всех валют в портфеле"""
        return CodeCurrencyListDTO.from_dict(cast(dict[str, list], self._currencies))

    def _update_currencies_list(self, currency_code: str) -> None:
        """Обновляет список валют, если переданной валюты нет в списке"""
        if not any(item["code"] == currency_code for item in self._currencies["items"]):
            self._currencies["items"].append({"code": currency_code})

    @property
    def data(self) -> CurrencyListDTO:
        """Получить курсы валют"""
        if self._exchange_rates is None:
            raise PortfolioError("Не известен курс валют")
        return CurrencyListDTO.from_dict(cast(dict[str, list], self._exchange_rates))

    @data.setter
    def data(self, dto: CurrencyListDTO) -> None:
        if not dto.items:
            raise PortfolioError("Передан пустой список курсов валют")
        self._exchange_rates = self._convert_to_typed_dict(
            data=dto.to_dict(),
            container_type=ExchangeRateData,
            item_type=CurrencyValueItem,
            required_keys=["code", "value"],
        )
        self._rates_index = self._build_index(
            items=[dict(item) for item in self._exchange_rates["items"]],
            key_field="code",
            value_field="value",
            value_converter=float,
        )

    @property
    def amount(self) -> AmountCurrencyListDTO:
        """Получить сумму каждой валюты"""
        return AmountCurrencyListDTO.from_dict(cast(dict[str, list], self._amount))

    @amount.setter
    def amount(self, dto: AmountCurrencyListDTO) -> None:
        if not dto.items:
            raise PortfolioError("Передан пустой список количества валют")
        self._amount = self._convert_to_typed_dict(
            data=dto.to_dict(),
            container_type=AmountData,
            item_type=CurrencyAmountItem,
            required_keys=["code", "amount"],
        )
        self._amount_index = self._build_index(
            items=[dict(item) for item in self._amount["items"]],
            key_field="code",
            value_field="amount",
            value_converter=float,
        )

    def get_amount_one(self, currency: str) -> float:
        """Получить количество указанной валюты."""
        if currency not in self._amount_index:
            raise PortfolioError(f"Валюта '{currency}' не найдена в портфеле")
        return self._amount_index[currency]

    def set_amount_one(self, dto: CurrencyAmountDTO) -> None:
        """Установить количество конкретной валюты."""
        if dto.amount < 0:
            raise PortfolioError("Невозможно установить отрицательное значение!")
        self._update_currencies_list(dto.code)
        items = self._amount["items"]
        updated = False

        for item in items:
            if item["code"] == dto.code:
                item["amount"] = dto.amount
                updated = True
                break

        if not updated:
            items.append({"code": dto.code, "amount": dto.amount})

        # Обновляем индекс
        self._amount_index[dto.code] = dto.amount

    def modify_amount_one(self, dto: UpdateCurrencyAmountDTO) -> CurrencyAmountDTO:
        currency_code = dto.code
        change_amount = dto.delta

        if currency_code not in self._amount_index:
            raise PortfolioError(f"Валюта '{currency_code}' не найдена в портфеле")

        new_amount = self._amount_index[currency_code] + change_amount
        if new_amount < 0:
            raise PortfolioError(
                f"Невозможно уменьшить количество валюты '{currency_code}' до отрицательного значения. "  # noqa: E501
                f"Текущее количество: {self._amount_index[currency_code]}, "
                f"попытка изменить на: {change_amount}"
            )

        updated = False
        for item in self._amount["items"]:
            if item["code"] == currency_code:
                item["amount"] = new_amount
                updated = True
                break

        if not updated:
            raise PortfolioError(
                f"Внутренняя ошибка: не удалось найти валюту '{currency_code}' для обновления"  # noqa: E501
            )

        self._amount_index[currency_code] = new_amount

        return CurrencyAmountDTO(code=currency_code, amount=new_amount)

    def set_multiple_amounts(
        self, amounts: AmountCurrencyListDTO
    ) -> AmountCurrencyListDTO:  # noqa: E501
        """Установить несколько валют одновременно"""
        if not amounts.items:
            raise PortfolioError("Передан пустой список валют")

        for item in amounts.items:
            if item.amount < 0:
                raise PortfolioError(
                    f"Невозможно установить отрицательное значение для {item.code}"
                )

        for item in amounts.items:
            self.set_amount_one(item)

        return amounts

    def modify_multiple_amounts(
        self, amounts: UpdateCurrencyAmountListDTO
    ) -> AmountCurrencyListDTO:  # noqa: E501
        """Изменить несколько валют одновременно"""
        if not amounts.items:
            raise PortfolioError("Передан пустой список изменений")

        for item in amounts.items:
            if item.code not in self._amount_index:
                raise PortfolioError(f"Валюта {item.code} не найдена в портфеле")
        updated_items = []
        for item in amounts.items:
            dto = self.modify_amount_one(
                UpdateCurrencyAmountDTO(code=item.code, delta=item.delta)
            )
            updated_items.append(dto)
        return AmountCurrencyListDTO(items=updated_items)

    def get_rate(self, currency: str) -> CurrencyDTO:
        """Получить курс валюты к рублю"""
        if self._rates_index is None:
            raise CurrencyNotFoundError("Курсы валют не установлены")
        if currency not in self._rates_index:
            raise CurrencyNotFoundError(f"Курс для валюты {currency} не найден")
        dto = CurrencyDTO(code=currency, value=self._rates_index[currency])
        return dto

    def update_rates(self, dto: CurrencyListDTO) -> None:
        """Обновляет курсы валют в портфеле.
        :param dto: CurrencyListDTO с новыми курсами валют
        """
        if not dto.items:
            raise PortfolioError("Необходимо передать как минимум один курс валюты")

        new_rates = self._convert_to_typed_dict(
            data=dto.to_dict(),
            container_type=ExchangeRateData,
            item_type=CurrencyValueItem,
            required_keys=["code", "value"],
        )

        required_currencies = {item["code"] for item in self._currencies["items"]}
        updated_currencies = {item["code"] for item in new_rates["items"]}

        missing_currencies = required_currencies - updated_currencies
        if missing_currencies:
            raise PortfolioError(
                f"Отсутствуют курсы для обязательных валют: {', '.join(missing_currencies)}"  # noqa: E501
            )

        for item in new_rates["items"]:
            if item["value"] <= 0:
                raise PortfolioError(
                    f"Курс валюты {item['code']} должен быть положительным числом, получено: {item['value']}"  # noqa: E501
                )

        self._exchange_rates = new_rates

        if self._rates_index is None:
            self._rates_index = {}

        self._rates_index.update(
            {item["code"]: item["value"] for item in new_rates["items"]}
        )

    def get_total(self, in_currency: str = "rub") -> TotalCurrencyDTO:
        """Получить общую сумму портфеля в указанной валюте"""
        if self._rates_index is None:
            raise PortfolioError("Курсы валют не установлены")

        in_currency = in_currency.upper()
        if in_currency not in self._rates_index and in_currency != "RUB":
            raise PortfolioError(f"Неизвестный курс для валюты {in_currency}")

        total = 0.0
        for currency, amount in self._amount_index.items():
            if currency == "RUB":
                rub_amount = amount
            else:
                rate = self._rates_index.get(currency)
                if rate is None:
                    logger.info(f"Пропускаем валюту {currency} - курс не известен")
                    continue
                rub_amount = amount * rate

            if in_currency == "RUB":
                total += rub_amount
            else:
                total += rub_amount / self._rates_index[in_currency]
        return TotalCurrencyDTO(code=in_currency, total_amount=round(total, 2))

    def get_portfolio_summary(self, in_currency: str = "rub") -> SummaryCurrencyDTO:
        """Получить полную сводку по портфелю"""
        if self._exchange_rates is None:
            raise PortfolioError("Курсы валют не установлены")

        rates_index = self._rates_index
        if rates_index is None:
            raise PortfolioError("Индекс курсов не инициализирован")

        filtered_amounts = []
        for item in self._amount["items"]:
            if item["code"] == "RUB" or item["code"] in rates_index:
                filtered_amounts.append(
                    CurrencyAmountDTO(code=item["code"], amount=item["amount"])
                )
        amounts = AmountCurrencyListDTO(items=filtered_amounts)
        rates = CurrencyListDTO.from_dict(self.data.to_dict())
        total = self.get_total(in_currency=in_currency)

        return SummaryCurrencyDTO(
            amounts=amounts,
            rates=rates,
            total=total,
        )

    def has_changes(self, previous_state: dict) -> bool:
        """Проверить, изменился ли портфель"""
        current_amounts = self._amount_index
        if previous_state.get("amounts") != current_amounts:
            return True

        if self._rates_index is not None:
            current_rates = self._rates_index
            return previous_state.get("rates") != current_rates

        return False
