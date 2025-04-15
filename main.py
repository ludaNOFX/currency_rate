import logging
import asyncio
import signal

from src.run_server import run_api_server
from run_service import run_currency_service

logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска"""
    # Обработка сигналов завершения
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def shutdown_handler():
        logger.info("Received shutdown signal")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown_handler)

    # Запускаем оба сервиса параллельно
    currency_task = asyncio.create_task(run_currency_service())
    api_task = asyncio.create_task(run_api_server())

    # Ждем сигнала завершения
    await stop_event.wait()

    # Корректное завершение
    currency_task.cancel()
    api_task.cancel()

    try:
        await asyncio.gather(currency_task, api_task, return_exceptions=True)
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

    logger.info("Service stopped gracefully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
