from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.stock_basic import StockBasic


class StockRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_code(self, stock_code: str, market: str) -> StockBasic | None:
        return (
            self.db.query(StockBasic)
            .filter(
                StockBasic.stock_code == stock_code,
                StockBasic.market == market,
            )
            .first()
        )

    def list_by_code(self, stock_code: str) -> list[StockBasic]:
        return (
            self.db.query(StockBasic)
            .filter(StockBasic.stock_code == stock_code)
            .order_by(StockBasic.market.asc())
            .all()
        )

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
