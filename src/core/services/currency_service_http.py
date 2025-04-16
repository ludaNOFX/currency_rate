from datetime import datetime, timedelta
import logging

from collections.abc import Callable
from typing import Optional

from core.dto.currency_dto import CurrencyListDTO
from core.exceptions import ServiceError
from core.interface.portfolio import IPortfolio
from core.interface.base_http_service import IBASEHTTPService


logger = logging.getLogger(__name__)


class CurrencyServiceHTTPUSECASE:
    def __init__(self, service: IBASEHTTPService, repo: IPortfolio) -> None:
        self._service = service
        self._repo = repo
        self._last_print_time = None
        self._last_state = None

    @property
    def service(self) -> IBASEHTTPService:
        return self._service

    @property
    def repo(self) -> IPortfolio:
        return self._repo

    async def __call__(
        self,
        *,
        debug: bool,
        url: str,
        items_key: Optional[str] = None,  # noqa: UP007
        field_map: Optional[dict[str, str]] = None,  # noqa: UP007
        filter_func: Optional[Callable[[dict], bool]] = None,  # noqa: UP007, E501
    ) -> CurrencyListDTO:
        self.service.configure(url=url, debug=debug)
        self._update_tracked_currencies()
        effective_filter = filter_func or self._default_filter
        try:
            res = await self.service.execute(
                items_key=items_key,
                field_map=field_map,
                filter_func=effective_filter,
            )
            self.repo.data = res
            logger.info("Currency rates successfully updated")
            current_time = datetime.now()
            if self._should_print_state(current_time, debug):
                self._print_current_state(debug)
                self._last_print_time = current_time
                self._last_state = self.repo.get_portfolio_summary()
            return res
        except Exception as e:
            logger.error(f"Request to {url} failed")
            if debug:
                logger.exception(f"Ошибка запроса на {url}")
            raise ServiceError("Ошибка в Service") from e

    def _should_print_state(self, current_time: datetime, debug) -> bool:
        if self._last_print_time is None:
            if debug:
                logger.debug("First print - showing state")
            return True

        time_passed = current_time - self._last_print_time
        if time_passed < timedelta(minutes=1):
            if debug:
                logger.debug(f"Only {time_passed.seconds}s passed - skipping")
            return False

        current_state = self.repo.get_portfolio_summary()
        state_changed = current_state != self._last_state

        if debug:
            logger.debug(f"Time passed: {time_passed}, changed: {state_changed}")

        return state_changed

    def _print_current_state(self, debug: bool) -> None:
        """Гибко выводит состояние портфеля для любых валют"""
        data = self.repo.get_portfolio_summary().to_dict()
        currencies = [item["code"] for item in data["amounts"]["items"]]
        base_currency = data["total"]["code"]  # RUB в вашем примере
        amounts = {item["code"]: item["amount"] for item in data["amounts"]["items"]}
        rates = {item["code"]: item["value"] for item in data["rates"]["items"]}

        output = ["\nCurrent state:"]
        for currency in currencies:
            output.append(f"{currency.lower()}: {amounts[currency]}")
        output.append("\nExchange rates:")
        for currency in rates:
            if currency != base_currency:
                output.append(
                    f"{base_currency.lower()}-{currency.lower()}: {rates[currency]}"
                )
        other_currencies = [c for c in rates if c != base_currency]
        for i in range(len(other_currencies)):
            for j in range(i + 1, len(other_currencies)):
                c1, c2 = other_currencies[i], other_currencies[j]
                cross_rate = rates[c2] / rates[c1]
                output.append(f"{c1.lower()}-{c2.lower()}: {cross_rate:.4f}")
        output.append("\nTotal value:")
        total_amount = data["total"]["total_amount"]

        for currency in [base_currency] + other_currencies:
            if currency == base_currency:
                value = total_amount
            else:
                value = total_amount / rates[currency]
            output.append(f"{value:.2f} {currency.lower()}")

        print("\n".join(output))

        if debug:
            logger.debug("Portfolio state printed for currencies: %s", currencies)

    def _update_tracked_currencies(self):
        """Обновляет список отслеживаемых валют из репозитория"""
        currencies = getattr(self.repo, "currencies", None)
        if currencies:
            self._tracked_currencies = {item.code for item in currencies.items}

    def _default_filter(self, item: dict) -> bool:
        """Функция фильтрации по умолчанию"""
        return item.get("CharCode") in self._tracked_currencies
