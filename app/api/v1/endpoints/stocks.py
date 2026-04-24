from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.stock import StockBasicResponse
from app.schemas.dividend import DividendItemResponse, DividendListResponse
from app.services.stock_service import StockService
from app.services.dividend_service import DividendService

router = APIRouter(prefix="/stocks", tags=["stocks"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{stock_code}", response_model=StockBasicResponse)
def get_stock_basic(stock_code: str, db: Session = Depends(get_db)):
    service = StockService(db)
    stock = service.get_stock_basic(stock_code)
    if not stock:
        raise HTTPException(status_code=404, detail={
            "code": "STOCK_NOT_FOUND",
            "message": f"Stock code {stock_code} not found."
        })
    return stock


@router.get("/{stock_code}/dividends", response_model=DividendListResponse)
def get_stock_dividends(
    stock_code: str,
    year_from: int | None = Query(default=None),
    year_to: int | None = Query(default=None),
    db: Session = Depends(get_db)
):
    if year_from and year_to and year_from > year_to:
        raise HTTPException(status_code=422, detail={
            "code": "INVALID_YEAR_RANGE",
            "message": "year_from cannot be greater than year_to."
        })

    stock_service = StockService(db)
    stock = stock_service.get_stock_basic(stock_code)
    if not stock:
        raise HTTPException(status_code=404, detail={
            "code": "STOCK_NOT_FOUND",
            "message": f"Stock code {stock_code} not found."
        })

    dividend_service = DividendService(db)
    items = dividend_service.list_dividends(stock_code, year_from, year_to)

    last_updated_at = max((item.updated_at for item in items), default=None)

    return {
        "stock_code": stock_code,
        "items": items,
        "last_updated_at": last_updated_at
    }
