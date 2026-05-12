from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class DividendSearchItemResponse(BaseModel):
    stock_code: str
    market: str
    company_name: str
    company_short_name: str | None = None

    industry: str | None = None
    industry_name: str | None = None

    dividend_year: int
    dividend_year_ad: int | None = None
    period_label: str | None = None

    cash_dividend_per_share: Decimal | None = None
    stock_dividend_per_share: Decimal | None = None
    total_dividend_per_share: Decimal | None = None


class DividendSearchListResponse(BaseModel):
    items: list[DividendSearchItemResponse]
    count: int
    total_count: int