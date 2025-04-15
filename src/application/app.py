import logging
from fastapi import FastAPI

from application.api.register_api import register_api_routes
from src.application.settings import settings
from src.application.logger_settings import logging_setup


logger = logging.getLogger(__name__)


def create_app():
    logging_setup(settings=settings)
    logger.info(f"Init app with ENV={settings.PROJ_ENV}")
    app = FastAPI(
        title=settings.TITLE,
        docs_url=f"{settings.GLOBAL_PREFIX_URL}/docs",
        openapi_url=f"{settings.GLOBAL_PREFIX_URL}/openapi.json",
        redoc_url=f"{settings.GLOBAL_PREFIX_URL}/redoc",
        debug=settings.DEBUG,
    )

    # middleware
    # TODO
    # routes
    register_api_routes(
        app=app,
        prefix=settings.GLOBAL_PREFIX_URL,
    )

    return app
