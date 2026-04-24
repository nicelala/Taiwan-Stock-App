from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.core.utils import now_utc


class DividendHistory(Base):
    __tablename__ = "dividend_history"
    __table_args__ = (
        UniqueConstraint("biz_key", name="uq_dividend_history_biz_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stock_basic.id"), nullable=False)

    stock_code: Mapped[str] = mapped_column(String(20), nullable=False)
    market: Mapped[str] = mapped_column(String(20), nullable=False, default="TWSE")

    dividend_year: Mapped[int] = mapped_column(Integer, nullable=False)
    belongs_to_year_or_period: Mapped[str | None] = mapped_column(String(50), nullable=True)
    period_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resolution_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    board_approved_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    shareholder_meeting_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    cash_dividend_per_share: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    stock_dividend_per_share: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    total_dividend_per_share: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    stock_dividend_rate_pct: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)

    par_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)

    source_name: Mapped[str] = mapped_column(String(50), nullable=False, default="TWSE_OPENAPI")
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    biz_key: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc, nullable=False)