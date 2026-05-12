from __future__ import annotations

from decimal import Decimal

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.models.dividend_history import DividendHistory
from app.models.stock_basic import StockBasic


class DividendRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_stock_code(
        self,
        stock_code: str,
        market: str,
        year_from: int | None = None,
        year_to: int | None = None,
    ):
        query = (
            self.db.query(DividendHistory)
            .filter(
                DividendHistory.stock_code == stock_code,
                DividendHistory.market == market,
            )
        )

        if year_from is not None:
            query = query.filter(DividendHistory.dividend_year >= year_from)

        if year_to is not None:
            query = query.filter(DividendHistory.dividend_year <= year_to)

        return query.order_by(
            DividendHistory.dividend_year.desc(),
            DividendHistory.id.desc(),
        ).all()

    def search(
        self,
        market: str | None = None,
        year: int | None = None,
        cash_min: Decimal | None = None,
        stock_min: Decimal | None = None,
        total_min: Decimal | None = None,
        sort_by: str = "total",
        sort_dir: str = "desc",
        limit: int = 20,
        offset: int = 0,
    ):
        base_query = self._build_search_query(
            market=market,
            year=year,
            cash_min=cash_min,
            stock_min=stock_min,
            total_min=total_min,
        )

        total_count = base_query.count()

        sort_column_map = {
            "cash": DividendHistory.cash_dividend_per_share,
            "stock": DividendHistory.stock_dividend_per_share,
            "total": DividendHistory.total_dividend_per_share,
            "year": DividendHistory.dividend_year,
            "code": StockBasic.stock_code,
        }

        sort_column = sort_column_map[sort_by]
        order_func = desc if sort_dir == "desc" else asc

        rows = (
            base_query.order_by(
                order_func(sort_column),
                StockBasic.stock_code.asc(),
                StockBasic.market.asc(),
                DividendHistory.id.desc(),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

        return rows, total_count

    def upsert_one(self, payload: dict) -> DividendHistory:
        obj = (
            self.db.query(DividendHistory)
            .filter(DividendHistory.biz_key == payload["biz_key"])
            .first()
        )

        if obj is None:
            obj = DividendHistory(**payload)
            self.db.add(obj)
            self.db.flush()
            return obj

        for key, value in payload.items():
            setattr(obj, key, value)

        self.db.flush()
        return obj

    # --------------------------------------------------
    # internal helpers
    # --------------------------------------------------

    def _build_search_query(
        self,
        market: str | None = None,
        year: int | None = None,
        cash_min: Decimal | None = None,
        stock_min: Decimal | None = None,
        total_min: Decimal | None = None,
    ):
        query = (
            self.db.query(DividendHistory, StockBasic)
            .join(StockBasic, DividendHistory.stock_id == StockBasic.id)
        )

        if market is not None:
            query = query.filter(DividendHistory.market == market)

        if year is not None:
            query = query.filter(DividendHistory.dividend_year == year)

        if cash_min is not None:
            query = query.filter(DividendHistory.cash_dividend_per_share >= cash_min)

        if stock_min is not None:
            query = query.filter(DividendHistory.stock_dividend_per_share >= stock_min)

        if total_min is not None:
            query = query.filter(DividendHistory.total_dividend_per_share >= total_min)

        return query