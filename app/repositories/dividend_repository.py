from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.dividend_history import DividendHistory


class DividendRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_stock_code(
        self,
        stock_code: str,
        market: str,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[DividendHistory]:
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
