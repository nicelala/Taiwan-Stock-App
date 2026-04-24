from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.schemas.stock import StockBasicResponse
from app.schemas.dividend import DividendListResponse
from app.services.stock_service import StockService
from app.services.dividend_service import DividendService

router = APIRouter(prefix="/api/v1")


@router.get("/stocks/{stock_code}", response_model=StockBasicResponse)
def get_stock_basic(
    stock_code: str,
    market: str | None = Query(default=None, description="TWSE or TPEX"),
    fetch_remote: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    service = StockService(db)

    try:
        stock = service.get_stock(stock_code, market)
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_MARKET",
                    "message": "market must be TWSE or TPEX",
                },
            )
        if str(exc) == "MULTIPLE_MARKET_MATCH":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "MULTIPLE_MARKET_MATCH",
                    "message": f"stock_code={stock_code} exists in multiple markets, please specify ?market=TWSE or ?market=TPEX",
                },
            )
        raise

    if stock is None and (fetch_remote or settings.auto_fetch_on_miss):
        try:
            stock = service.sync_one_if_missing(stock_code, market)
        except ValueError as exc:
            if str(exc) == "INVALID_MARKET":
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "INVALID_MARKET",
                        "message": "market must be TWSE or TPEX",
                    },
                )
            if str(exc) == "MULTIPLE_MARKET_MATCH":
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "MULTIPLE_MARKET_MATCH",
                        "message": f"stock_code={stock_code} exists in multiple markets, please specify ?market=TWSE or ?market=TPEX",
                    },
                )
            raise

    if stock is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "STOCK_NOT_FOUND",
                "message": f"stock_code={stock_code} not found in local DB",
            },
        )

    return stock


@router.get("/stocks/{stock_code}/dividends", response_model=DividendListResponse)
def get_stock_dividends(
    stock_code: str,
    market: str | None = Query(default=None, description="TWSE or TPEX"),
    year_from: int | None = Query(default=None),
    year_to: int | None = Query(default=None),
    fetch_remote: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    if year_from is not None and year_to is not None and year_from > year_to:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_YEAR_RANGE",
                "message": "year_from cannot be greater than year_to",
            },
        )

    stock_service = StockService(db)

    try:
        stock = stock_service.get_stock(stock_code, market)
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_MARKET",
                    "message": "market must be TWSE or TPEX",
                },
            )
        if str(exc) == "MULTIPLE_MARKET_MATCH":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "MULTIPLE_MARKET_MATCH",
                    "message": f"stock_code={stock_code} exists in multiple markets, please specify ?market=TWSE or ?market=TPEX",
                },
            )
        raise

    if stock is None and (fetch_remote or settings.auto_fetch_on_miss):
        try:
            stock = stock_service.sync_one_if_missing(stock_code, market)
        except ValueError as exc:
            if str(exc) == "INVALID_MARKET":
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "INVALID_MARKET",
                        "message": "market must be TWSE or TPEX",
                    },
                )
            if str(exc) == "MULTIPLE_MARKET_MATCH":
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "MULTIPLE_MARKET_MATCH",
                        "message": f"stock_code={stock_code} exists in multiple markets, please specify ?market=TWSE or ?market=TPEX",
                    },
                )
            raise

    if stock is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "STOCK_NOT_FOUND",
                "message": f"stock_code={stock_code} not found in local DB",
            },
        )

    dividend_service = DividendService(db)
    resolved_market = stock.market

    try:
        items = dividend_service.list_dividends(
            stock_code=stock_code,
            market=resolved_market,
            year_from=year_from,
            year_to=year_to,
        )
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_MARKET",
                    "message": "market must be TWSE or TPEX",
                },
            )
        raise

    if not items and (fetch_remote or settings.auto_fetch_on_miss):
        try:
            items = dividend_service.sync_one_if_missing(stock_code, resolved_market)
        except ValueError as exc:
            if str(exc) == "INVALID_MARKET":
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "INVALID_MARKET",
                        "message": "market must be TWSE or TPEX",
                    },
                )
            raise

        if year_from is not None or year_to is not None:
            items = dividend_service.list_dividends(
                stock_code=stock_code,
                market=resolved_market,
                year_from=year_from,
                year_to=year_to,
            )

    return {
        "stock_code": stock_code,
        "market": resolved_market,
        "items": items,
    }


@router.post("/admin/refresh/stocks")
def refresh_stock_basic(
    market: str = Query(default="TWSE", description="TWSE or TPEX"),
    db: Session = Depends(get_db),
):
    service = StockService(db)

    try:
        result = service.sync_from_source(market)
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_MARKET",
                    "message": "market must be TWSE or TPEX",
                },
            )
        raise

    return result


@router.post("/admin/refresh/dividends")
def refresh_dividends(
    market: str = Query(default="TWSE", description="TWSE or TPEX"),
    db: Session = Depends(get_db),
):
    stock_service = StockService(db)
    dividend_service = DividendService(db)

    try:
        stock_service.sync_from_source(market)
        result = dividend_service.sync_from_source(market)
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_MARKET",
                    "message": "market must be TWSE or TPEX",
                },
            )
        if str(exc) == "MULTIPLE_MARKET_MATCH":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "MULTIPLE_MARKET_MATCH",
                    "message": "multiple market match",
                },
            )
        raise

    return result
