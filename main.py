import logging
import asyncio
import signal

from run_api import run_api_server
from run_service import run_currency_service

logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска"""
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def shutdown_handler():
        logger.info("Received shutdown signal")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown_handler)

    currency_task = asyncio.create_task(run_currency_service(stop_event))
    api_task = asyncio.create_task(run_api_server(stop_event))

    await stop_event.wait()

    currency_task.cancel()
    api_task.cancel()

    try:
        await asyncio.gather(currency_task, api_task, return_exceptions=True)
    except Exception:
        logger.error("Error during shutdown")
    finally:
        logger.info("Service stopped gracefully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
