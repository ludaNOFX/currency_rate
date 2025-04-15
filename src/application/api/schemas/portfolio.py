from collections.abc import Sequence
from pydantic import BaseModel


class CurrencySchema(BaseModel):
    code: str


class CurrencyValueSchema(CurrencySchema):
    value: float


class CurrencyAmountSchema(CurrencySchema):
    amount: float


class UpdatedCurrencyAmountSchema(CurrencySchema):
    delta: float


class AmountCurrencyListSchema(BaseModel):
    items: Sequence[CurrencyAmountSchema]


class UpdatedAmountCurrencyListSchema(BaseModel):
    items: Sequence[UpdatedCurrencyAmountSchema]


class CurrencyValueListSchema(BaseModel):
    items: Sequence[CurrencyValueSchema]


class TotalCurrencySchema(CurrencySchema):
    total_amount: float


class SummaryCurrencySchema(BaseModel):
    amounts: AmountCurrencyListSchema
    rates: CurrencyValueListSchema
    total: TotalCurrencySchema
