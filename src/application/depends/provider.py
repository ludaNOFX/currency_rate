from core.interface.portfolio import IPortfolio
from application.state import app_state


def get_repo() -> IPortfolio:
    """Dependency для получения репозитория"""
    return app_state.get_repo()
