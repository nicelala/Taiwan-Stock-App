from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.utils import get_industry_name
from app.repositories.stock_repository import StockRepository


class StockSearchService:
    VALID_MARKETS = {"TWSE", "TPEX"}

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = StockRepository(db)

    def search(
        self,
        q: str,
        market: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ):
        normalized_q = self._normalize_query(q)
        normalized_market = self._normalize_market(market)
        normalized_limit = self._normalize_limit(limit)
        normalized_offset = self._normalize_offset(offset)

        rows = self.repo.search(
            q=normalized_q,
            market=normalized_market,
            limit=normalized_limit,
            offset=normalized_offset,
        )

        return self._attach_derived_fields_list(rows)

    # --------------------------------------------------
    # internal helpers
    # --------------------------------------------------

    def _normalize_query(self, q: str | None) -> str:
        if q is None:
            raise ValueError("INVALID_QUERY")

        text = str(q).strip()
        if not text:
            raise ValueError("INVALID_QUERY")

        return text

    def _normalize_market(self, market: str | None) -> str | None:
        if market is None:
            return None

        text = str(market).strip().upper()
        if text not in self.VALID_MARKETS:
            raise ValueError("INVALID_MARKET")

        return text

    def _normalize_limit(self, limit: int | None) -> int:
        if limit is None:
            return 20

        try:
            value = int(limit)
        except Exception:
            return 20

        if value < 1:
            return 1

        if value > 100:
            return 100

        return value

    def _normalize_offset(self, offset: int | None) -> int:
        if offset is None:
            return 0

        try:
            value = int(offset)
        except Exception:
            return 0

        if value < 0:
            return 0

        return value

    def _attach_derived_fields_list(self, rows: list):
        for row in rows:
            row.industry_name = get_industry_name(row.industry)
        return rows