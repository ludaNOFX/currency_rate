import asyncio
import logging
import uvicorn

from application.settings import settings


logger = logging.getLogger(__name__)


async def run_api_server(stop_event: asyncio.Event):
    """Запускает FastAPI сервер"""
    config = uvicorn.Config(
        "src.application.app:create_app",
        host="0.0.0.0",
        port=8000,
        log_level="debug" if settings.DEBUG else "info",
        reload=settings.DEBUG,
        lifespan="off",
    )
    server = uvicorn.Server(config)

    server_task = asyncio.create_task(server.serve())
    stop_task = asyncio.create_task(stop_event.wait())

    try:
        done, _ = await asyncio.wait(
            [server_task, stop_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        if stop_task in done:
            logger.info("Stop event received, shutting down API server...")
            server.should_exit = True
            try:
                await server_task
            except asyncio.CancelledError:
                logger.info("API server shutdown was cancelled gracefully.")
                return
    except asyncio.CancelledError:
        logger.info("run_api_server cancelled.")
    except Exception as e:
        logger.error(f"Unexpected error in run_api_server: {e}")
