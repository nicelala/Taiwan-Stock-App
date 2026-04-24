from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.core.utils import now_utc


class StockBasic(Base):
    __tablename__ = "stock_basic"
    __table_args__ = (
        UniqueConstraint("stock_code", "market", name="uq_stock_basic_code_market"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    stock_code: Mapped[str] = mapped_column(String(20), nullable=False)
    market: Mapped[str] = mapped_column(String(20), nullable=False, default="TWSE")

    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    company_short_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)

    par_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    listing_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    capital_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    issued_common_shares: Mapped[int | None] = mapped_column(Integer, nullable=True)

    source_name: Mapped[str] = mapped_column(String(50), nullable=False, default="TWSE_OPENAPI")
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc, nullable=False)