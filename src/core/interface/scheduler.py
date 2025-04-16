from abc import ABC, abstractmethod
from collections.abc import Coroutine
from typing import Optional


class IScheduler(ABC):
    @abstractmethod
    async def start(self, *args, kwargs: dict) -> Optional[Coroutine]: ...  # noqa: UP007

    @abstractmethod
    async def _run(self, *args, **kwargs) -> Optional[Coroutine]: ...  # noqa: UP007

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    async def shutdown(self) -> None: ...
