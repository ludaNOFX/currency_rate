# utils/scheduler.py
import asyncio
from collections.abc import Callable, Coroutine
import logging
from typing import Optional

from core.interface.scheduler import IScheduler


logger = logging.getLogger(__name__)


class Scheduler(IScheduler):
    def __init__(self, task: Callable, interval: int):
        self._task = task
        self._interval = interval
        self._is_running = False
        self._current_task: Optional[asyncio.Task] = None  # noqa: UP007
        self._stop_event = asyncio.Event()

    async def start(self, *args, kwargs: dict) -> Optional[Coroutine]:  # noqa: UP007
        """Start the scheduler and return the last result when stopped."""
        if self._is_running:
            raise RuntimeError("Scheduler is already running")

        self._is_running = True
        self._stop_event.clear()
        self._current_task = asyncio.create_task(self._run(*args, **kwargs))

        try:
            return await self._current_task
        except asyncio.CancelledError:
            logger.debug("Scheduler task was cancelled")
            return None
        except Exception as e:
            logger.error(f"Error in scheduler task: {e}")
            raise

    async def _run(self, *args, **kwargs) -> Optional[Coroutine]:  # noqa: UP007
        """Internal task runner."""
        last_result = None
        try:
            while self._is_running:
                try:
                    last_result = await self._task(*args, **kwargs)
                except asyncio.CancelledError:
                    logger.debug("Task execution was cancelled")
                    raise
                except Exception as e:
                    logger.error(f"Error executing scheduled task: {e}")
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(), timeout=self._interval
                    )
                    break
                except asyncio.CancelledError:
                    logger.debug("Wait was cancelled")
                    raise
                except TimeoutError:
                    continue
        finally:
            self._is_running = False
            logger.debug("Scheduler loop stopped")
        return last_result

    def stop(self) -> None:
        """Stop the scheduler gracefully."""
        if self._is_running and not self._stop_event.is_set():
            self._is_running = False
            self._stop_event.set()
            if self._current_task and not self._current_task.done():
                self._current_task.cancel()

    async def _wait_until_stopped(self) -> None:
        if self._current_task:
            try:  # noqa: SIM105
                await self._current_task
            except asyncio.CancelledError:
                logger.info("Task was cancelled during shutdown.")

    async def shutdown(self) -> None:
        self.stop()
        await self._wait_until_stopped()
