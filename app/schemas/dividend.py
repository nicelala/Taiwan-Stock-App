from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DividendItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dividend_year: int
    belongs_to_year_or_period: str | None = None
    period_label: str | None = None
    resolution_status: str | None = None
    board_approved_date: date | None = None
    shareholder_meeting_date: date | None = None

    cash_dividend_per_share: Decimal | None = None
    stock_dividend_per_share: Decimal | None = None
    total_dividend_per_share: Decimal | None = None
    stock_dividend_rate_pct: Decimal | None = None

    par_value: Decimal | None = None
    updated_at: datetime


class DividendListResponse(BaseModel):
    stock_code: str
    market: str
    items: list[DividendItemResponse]