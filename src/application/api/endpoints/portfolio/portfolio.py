import logging
from fastapi import APIRouter, Depends, HTTPException

from application.api.schemas.portfolio import (
    AmountCurrencyListSchema,
    CurrencyValueSchema,
    SummaryCurrencySchema,
    UpdatedAmountCurrencyListSchema,
)
from application.depends.provider import get_repo
from core.dto.currency_dto import AmountCurrencyListDTO, UpdateCurrencyAmountListDTO
from core.exceptions import CurrencyNotFoundError, PortfolioError
from core.interface.portfolio import IPortfolio
from core.usecases import (
    get_currency_usecase,
    get_full_amount_usecase,
    modify_amount_usecase,
    set_amount_usecase,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{currency}",
    responses={
        200: {"model": CurrencyValueSchema},
    },
)
async def get_currency(
    currency: str,
    repo: IPortfolio = Depends(get_repo),
):
    try:
        uc = get_currency_usecase.Usecase(repo=repo)
        res = await uc(currency)
        response_schema = CurrencyValueSchema(**res.to_dict())
        return response_schema
    except CurrencyNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get(
    "/amount/get",
    responses={
        200: {"model": SummaryCurrencySchema},
    },
)
async def get_full_amount(repo: IPortfolio = Depends(get_repo)):
    try:
        uc = get_full_amount_usecase.Usecase(repo=repo)
        res = await uc()
        response_schema = SummaryCurrencySchema(**res.to_dict())
        return response_schema
    except PortfolioError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/amount/set",
    responses={
        200: {"model": AmountCurrencyListSchema},
    },
)
async def set_amount(
    schema: AmountCurrencyListSchema,
    repo: IPortfolio = Depends(get_repo),
):
    try:
        uc = set_amount_usecase.Usecase(repo=repo)
        print(schema)
        data = schema.model_dump()
        print(data)
        dto = AmountCurrencyListDTO.from_dict(data)
        print(dto)
        res = await uc(dto=dto)
        response_schema = AmountCurrencyListSchema(**res.to_dict())
        return response_schema
    except PortfolioError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.put(
    "/amount/modify",
    responses={
        200: {"model": AmountCurrencyListSchema},
    },
)
async def modify(
    schema: UpdatedAmountCurrencyListSchema,
    repo: IPortfolio = Depends(get_repo),
):
    try:
        uc = modify_amount_usecase.Usecase(repo=repo)
        data = schema.model_dump()
        print(data)
        dto = UpdateCurrencyAmountListDTO.from_dict(data)
        print(dto)
        res = await uc(dto=dto)
        response_schema = AmountCurrencyListSchema(**res.to_dict())
        return response_schema
    except PortfolioError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
