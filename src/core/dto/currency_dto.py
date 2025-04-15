from dataclasses import dataclass

from core.dto.base_dto import BaseDTO, BaseListDTO


@dataclass
class CodeCurrencyDTO(BaseDTO):
    code: str


@dataclass
class CurrencyDTO(CodeCurrencyDTO):
    value: float


@dataclass
class CurrencyAmountDTO(CodeCurrencyDTO):
    amount: float


@dataclass
class UpdateCurrencyAmountDTO(CodeCurrencyDTO):
    delta: float


@dataclass
class UpdateCurrencyAmountListDTO(BaseListDTO[UpdateCurrencyAmountDTO]): ...


@dataclass
class CurrencyListDTO(BaseListDTO[CurrencyDTO]): ...


@dataclass
class CodeCurrencyListDTO(BaseListDTO[CodeCurrencyDTO]): ...


@dataclass
class AmountCurrencyListDTO(BaseListDTO[CurrencyAmountDTO]): ...


@dataclass
class TotalCurrencyDTO(CodeCurrencyDTO):
    total_amount: float


@dataclass
class SummaryCurrencyDTO(BaseDTO):
    amounts: AmountCurrencyListDTO
    rates: CurrencyListDTO
    total: TotalCurrencyDTO
