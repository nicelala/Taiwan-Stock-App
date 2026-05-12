from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class StockBasicResponse(BaseModel):
    stock_code: str
    market: str
    company_name: str
    company_short_name: str | None = None
    industry: str | None = None
    industry_name: str | None = None
    par_value: Decimal | None = None
    capital_amount: int | None = None
    issued_common_shares: int | None = None
    listing_date: date | None = None


class StockSearchItemResponse(BaseModel):
    stock_code: str
    market: str
    company_name: str
    company_short_name: str | None = None
    industry: str | None = None
    industry_name: str | None = None
    listing_date: date | None = None


class StockSearchListResponse(BaseModel):
    items: list[StockSearchItemResponse]
    count: int
    total_count: int