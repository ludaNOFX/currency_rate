# src/application/state.py
from typing import Optional
from core.exceptions import AppStateError
from core.interface.portfolio import IPortfolio


class AppState:
    def __init__(self):
        self.repo_portfolio: Optional[IPortfolio] = None  # noqa: UP007

    def get_repo(self) -> IPortfolio:
        if self.repo_portfolio is None:
            raise AppStateError("Ошибка Состояния приложения не доступен Repo")
        return self.repo_portfolio


app_state = AppState()
