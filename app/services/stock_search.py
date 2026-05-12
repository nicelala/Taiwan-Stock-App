from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class StockSearchItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stock_code: str
    market: str
    company_name: str
    company_short_name: str | None = None
    industry: str | None = None
    industry_name: str | None = None
    listing_date: date | None = None


class StockSearchListResponse(BaseModel):
    count: int
    total_count: int
