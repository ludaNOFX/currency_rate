from abc import ABC, abstractmethod

from core.dto.currency_dto import (
    AmountCurrencyListDTO,
    CodeCurrencyListDTO,
    CurrencyAmountDTO,
    CurrencyDTO,
    CurrencyListDTO,
    SummaryCurrencyDTO,
    TotalCurrencyDTO,
    UpdateCurrencyAmountListDTO,
)


class IPortfolio(ABC):
    @property
    @abstractmethod
    def currencies(self) -> CodeCurrencyListDTO: ...

    @property
    @abstractmethod
    def data(self) -> CurrencyListDTO: ...

    @data.setter
    @abstractmethod
    def data(self, dto: CurrencyListDTO) -> None: ...

    @property
    @abstractmethod
    def amount(self) -> AmountCurrencyListDTO: ...

    @amount.setter
    @abstractmethod
    def amount(self, dto: AmountCurrencyListDTO) -> None: ...

    @abstractmethod
    def get_amount_one(self, currency: str) -> float: ...

    @abstractmethod
    def set_amount_one(self, dto: CurrencyAmountDTO) -> None: ...

    @abstractmethod
    def modify_amount_one(self, dto: CurrencyAmountDTO) -> None: ...

    @abstractmethod
    def set_multiple_amounts(
        self, amounts: AmountCurrencyListDTO
    ) -> AmountCurrencyListDTO:  # noqa: E501
        ...

    @abstractmethod
    def modify_multiple_amounts(
        self, amounts: UpdateCurrencyAmountListDTO
    ) -> AmountCurrencyListDTO:  # noqa: E501
        ...

    @abstractmethod
    def get_rate(self, currency: str) -> CurrencyDTO: ...

    @abstractmethod
    def update_rates(self, dto: CurrencyListDTO) -> None: ...

    @abstractmethod
    def get_total(self, in_currency: str = "rub") -> TotalCurrencyDTO: ...

    @abstractmethod
    def get_portfolio_summary(self, in_currency: str = "rub") -> SummaryCurrencyDTO: ...
