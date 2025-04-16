import asyncio
import logging

from application.logger_settings import logging_setup
from application.settings import settings
from core.services.currency_service_http import CurrencyServiceHTTPUSECASE
from depends.dep import create_repo_portfolio, create_scheduler, currency_http, json_keys
from shared.arg_parse import mapper_args, parse_args
from application.state import app_state


logger = logging.getLogger(__name__)


async def run_currency_service(stop_event: asyncio.Event):
    """Запускает сервис обновления курсов валют"""
    amounts_dict, currencies_dict, period, debug = parse_args()
    settings.DEBUG = debug
    logging_setup(settings=settings)
    logger.info("Currency service starting with debug=%s", debug)

    dto_amount, dto_currency = mapper_args(amounts_dict, currencies_dict)
    app_state.repo_portfolio = create_repo_portfolio(
        initial_amounts=dto_amount, currencies=dto_currency
    )

    currency_service = currency_http()
    uc = CurrencyServiceHTTPUSECASE(
        currency_service,
        app_state.repo_portfolio,
    )
    scheduler = create_scheduler(task=uc.__call__, interval=period)

    kwargs = {
        "url": settings.URL,
        "debug": debug,
        "items_key": "Valute",
        "field_map": json_keys(),
    }

    scheduler_task = asyncio.create_task(scheduler.start(kwargs=kwargs))
    stop_task = asyncio.create_task(stop_event.wait())
    try:
        done, _ = await asyncio.wait(
            [scheduler_task, stop_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        if stop_task in done:
            logger.info("Stop event received, shutting down Currency service...")
            try:
                await scheduler_task
            except asyncio.CancelledError:
                logger.info("Currency service shutdown was cancelled gracefully.")
                return
    except asyncio.CancelledError:
        logger.info("run_currency_service cancelled.")
    except Exception as e:
        logger.error(f"Unexpected error in run_cureency_service: {e}")

    if stop_task in done:
        logger.info("Stop event received, shutting down scheduler...")
        await scheduler.shutdown()
