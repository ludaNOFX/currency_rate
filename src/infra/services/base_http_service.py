import logging
import httpx
from collections.abc import Callable
from typing import Generic, Optional

from core.exceptions import ServiceError
from src.core.interface.base_http_service import IBASEHTTPService
from src.core.dto.base_dto import ListDTO

logger = logging.getLogger(__name__)


class BASEHTTPService(IBASEHTTPService, Generic[ListDTO]):
    list_dto: type[ListDTO]

    def __init__(self) -> None:
        self._url: Optional[str] = None  # noqa: UP007
        self._debug: bool = False

    def configure(self, url: str, debug: bool) -> None:
        """Конфигурация сервиса с URL и режимом отладки"""
        self._url = url
        self._debug = debug
        if self._debug:
            logger.info("Service configured in debug mode for URL: %s", url)

    @property
    def url(self) -> str:
        if self._url is not None:
            return self._url
        raise NotImplementedError("URL not configured")

    async def execute(
        self,
        *,
        items_key: Optional[str] = None,  # noqa: UP007
        field_map: Optional[dict[str, str]] = None,  # noqa: UP007
        filter_func: Optional[Callable[[dict], bool]] = None,  # noqa: UP007
    ) -> ListDTO:
        """Выполняет HTTP-запрос с логированием в debug-режиме"""
        try:
            async with httpx.AsyncClient() as client:
                # Логируем запрос если в debug-режиме
                if self._debug:
                    logger.debug("Making GET request to: %s", self.url)
                    logger.debug("Request headers: %s", client.headers)

                response = await client.get(self.url)

                # Логируем ответ если в debug-режиме
                if self._debug:
                    logger.debug("Response status: %s", response.status_code)
                    logger.debug("Response headers: %s", response.headers)
                    logger.debug(
                        "Response body (first 200 chars): %.200s...", response.text
                    )

                data = response.json()

                # Логируем полученные данные
                logger.info("Currency rates successfully received")
                if self._debug:
                    logger.debug("Full response data: %s", data)

                # Преобразуем в DTO
                dto = self.list_dto.from_dict(
                    data=data,
                    items_key=items_key,
                    field_map=field_map,
                    filter_func=filter_func,
                )

                return dto

        except httpx.HTTPError as e:
            error_msg = f"HTTP request failed to {self.url}"
            if self._debug:
                logger.exception(error_msg)
            else:
                logger.error("%s: %s", error_msg, str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error during request processing")
            if self._debug:
                logger.exception("Error details:")
            raise ServiceError("SERVICE HTTP ERROR") from e
