import logging

from application.logger_settings import logging_setup
from application.settings import settings
from core.services.currency_service_http import CurrencyServiceHTTP
from depends.dep import create_repo_portfolio, currency_http, json_keys
from shared.arg_parse import mapper_args, parse_args
from application.state import app_state
from shared.sheduler import Scheduler

logger = logging.getLogger(__name__)


async def run_currency_service():
    """Запускает сервис обновления курсов валют"""
    amounts_dict, currencies_dict, period, debug = parse_args()
    settings.DEBUG = debug
    logging_setup(settings=settings)
    logger.info("Currency service starting with debug=%s", debug)

    dto_amount, dto_curr = mapper_args(amounts_dict, currencies_dict)
    app_state.repo_portfolio = create_repo_portfolio(
        initial_amounts=dto_amount, currencies=dto_curr
    )

    currency_service = currency_http()
    service = CurrencyServiceHTTP(
        currency_service,
        app_state.repo_portfolio,
    )

    scheduler = Scheduler(
        task=service.__call__,
        interval=period,
    )

    kwargs = {
        "url": settings.URL,
        "debug": debug,
        "items_key": "Valute",
        "field_map": json_keys(),
    }

    await scheduler.start(kwargs=kwargs)
