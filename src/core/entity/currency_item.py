from typing import TypedDict


class CurrencyItem(TypedDict):
    code: str


class CurrencyAmountItem(CurrencyItem):
    amount: float


class CurrencyValueItem(CurrencyItem):
    value: float


class AmountData(TypedDict):
    items: list[CurrencyAmountItem]


class CurrencyData(TypedDict):
    items: list[CurrencyItem]


class ExchangeRateData(TypedDict):
    items: list[CurrencyValueItem]
