from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class StockBasicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stock_code: str
    market: str
    company_name: str
    company_short_name: str | None = None
    industry: str | None = None
    par_value: Decimal | None = None
    listing_date: date | None = None
    capital_amount: int | None = None
    issued_common_shares: int | None = None
    updated_at: datetime