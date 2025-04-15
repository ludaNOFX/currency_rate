# utils/scheduler.py
import asyncio
import signal
from collections.abc import Callable
from typing import Any, Optional


class Scheduler:
    def __init__(self, task: Callable, interval: int):
        self._task = task
        self._interval = interval
        self._is_running = False
        self._current_task: Optional[asyncio.Task] = None  # noqa: UP007
        self._stop_event = asyncio.Event()

    async def start(self, *args, kwargs: dict) -> Any:
        """Start the scheduler and return the last result when stopped."""
        if self._is_running:
            raise RuntimeError("Scheduler is already running")

        self._is_running = True
        self._stop_event.clear()
        self._current_task = asyncio.create_task(self._run(*args, **kwargs))

        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self.stop)

        try:
            return await self._current_task
        except asyncio.CancelledError:
            return None
        finally:
            # Clean up signal handlers
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.remove_signal_handler(sig)

    async def _run(self, *args, **kwargs) -> Any:
        """Internal task runner."""
        last_result = None
        try:
            while self._is_running:
                last_result = await self._task(*args, **kwargs)

                # Wait for interval or stop event
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(), timeout=self._interval
                    )
                    break  # Stop event was set
                except TimeoutError:
                    continue  # Interval elapsed, continue running
        finally:
            self._is_running = False
        return last_result

    def stop(self):
        """Stop the scheduler gracefully."""
        if self._is_running and not self._stop_event.is_set():
            self._is_running = False
            self._stop_event.set()
            if self._current_task and not self._current_task.done():
                self._current_task.cancel()
