from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.stock_basic import StockBasic


class StockRepository:
    
    def __init__(self, db: Session) -> None:
            self.db = db

    def get_by_code(self, stock_code: str, market: str | None = None):
        query = self.db.query(StockBasic).filter(StockBasic.stock_code == stock_code)

        if market is not None:
            return query.filter(StockBasic.market == market).first()

        return query.order_by(StockBasic.market.asc()).all()

    def search(
        self,
        q: str,
        market: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ):
        base_query = self._build_search_query(q=q, market=market)
        total_count = base_query.count()

        rows = (
            base_query.order_by(
                StockBasic.stock_code.asc(),
                StockBasic.market.asc(),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

        return rows, total_count

    def upsert_one(self, payload: dict) -> StockBasic:
        obj = (
            self.db.query(StockBasic)
            .filter(
                StockBasic.stock_code == payload["stock_code"],
                StockBasic.market == payload["market"],
            )
            .first()
        )

        if obj is None:
            obj = StockBasic(**payload)
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

    def _build_search_query(self, q: str, market: str | None = None):
        query = self.db.query(StockBasic)

        if market is not None:
            query = query.filter(StockBasic.market == market)

        keyword = str(q).strip()
        if keyword:
            query = query.filter(
                or_(
                    StockBasic.stock_code.like(f"{keyword}%"),
                    StockBasic.company_name.like(f"%{keyword}%"),
                    StockBasic.company_short_name.like(f"%{keyword}%"),
                )
            )

        return query