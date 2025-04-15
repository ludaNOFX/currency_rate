from core.dto.currency_dto import CurrencyListDTO
from infra.services.base_http_service import BASEHTTPService


class CurrencyHTTP(BASEHTTPService[CurrencyListDTO]):
    list_dto = CurrencyListDTO
