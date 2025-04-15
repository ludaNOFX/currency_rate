import argparse

from core.dto.currency_dto import AmountCurrencyListDTO, CodeCurrencyListDTO


def parse_args() -> tuple[dict, dict, int, bool]:
    parser = argparse.ArgumentParser(description="Currency tracking service")
    parser.add_argument("--rub", type=float, help="Initial amount in RUB")
    parser.add_argument("--usd", type=float, help="Initial amount in USD")
    parser.add_argument("--eur", type=float, help="Initial amount in EUR")
    parser.add_argument(
        "--period", type=int, required=True, help="Update interval in minutes"
    )
    parser.add_argument(
        "--debug",
        type=str,
        default="False",
        help="Enable debug mode (0/1/true/false/True/False/y/n/Y/N)",
    )

    args = parser.parse_args()
    validate_args(args)
    amounts_dict = {
        "items": [
            {"code": "RUB", "amount": args.rub} if args.rub is not None else None,
            {"code": "USD", "amount": args.usd} if args.usd is not None else None,
            {"code": "EUR", "amount": args.eur} if args.eur is not None else None,
        ]
    }
    amounts_dict["items"] = [item for item in amounts_dict["items"] if item is not None]
    currencies_dict = {
        "items": [{"code": item["code"]} for item in amounts_dict["items"] if item]
    }
    return amounts_dict, currencies_dict, args.period, args.debug


def validate_args(args):
    if args.rub is None and args.usd is None and args.eur is None:
        raise ValueError("At least one currency must be specified")
    for currency in ["rub", "usd", "eur"]:
        value = getattr(args, currency)
        if value is not None and value < 0:
            raise ValueError(f"Amount for {currency.upper()} cannot be negative")
    if args.period <= 0:
        raise ValueError("Period must be a positive number")
    debug_state = args.debug.lower() in ("1", "true", "y", "yes")
    args.debug = debug_state


def mapper_args(
    amounts_dict: dict,
    currencies_dict: dict,
) -> tuple[AmountCurrencyListDTO, CodeCurrencyListDTO]:
    dto_amount = AmountCurrencyListDTO.from_dict(amounts_dict)
    dto_curr = CodeCurrencyListDTO.from_dict(currencies_dict)
    return dto_amount, dto_curr
