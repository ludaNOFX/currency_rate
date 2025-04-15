from abc import ABC, abstractmethod

from collections.abc import Callable
from typing import Generic, Optional, TypeVar

from core.dto.base_dto import BaseListDTO

T = TypeVar("T", bound="BaseListDTO")


class IBASEHTTPService(ABC, Generic[T]):
    list_dto: type[T]

    @abstractmethod
    def configure(self, url: str, debug: bool) -> None: ...

    @property
    @abstractmethod
    def url(self) -> str: ...

    @abstractmethod
    async def execute(
        self,
        *,
        items_key: Optional[str] = None,  # noqa: UP007
        field_map: Optional[dict[str, str]] = None,  # noqa: UP007
        filter_func: Optional[Callable[[dict], bool]] = None,  # noqa: UP007, E501
    ) -> T: ...
