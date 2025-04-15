from typing import Optional


class BaseError(Exception):
    """Базовая ошибка"""

    def __init__(self, messsage: str, h: Optional[str] = ""):  # noqa: UP007
        self.message = messsage
        self.hidden = h
        super().__init__(self.message)


class PortfolioError(BaseError):
    """Ошибка Portfolio"""


class UsecaseError(BaseError):
    """Ошибка Usecase"""


class ServiceError(BaseError):
    """Ошибка Usecase"""


class AppStateError(BaseError):
    """Ошибка Состояния приложения не доступен Repo"""


class CurrencyNotFoundError(BaseError): ...
