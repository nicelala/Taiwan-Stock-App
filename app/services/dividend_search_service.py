from __future__ import annotations

from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.utils import get_ad_year, get_industry_name
from app.repositories.dividend_repository import DividendRepository


class DividendSearchService:
    VALID_MARKETS = {"TWSE", "TPEX"}
    VALID_SORT_BY = {"cash", "stock", "total", "year", "code"}
    VALID_SORT_DIR = {"asc", "desc"}

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = DividendRepository(db)

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
        normalized_market = self._normalize_market(market)
        normalized_sort_by = self._normalize_sort_by(sort_by)
        normalized_sort_dir = self._normalize_sort_dir(sort_dir)
        normalized_limit = self._normalize_limit(limit)
        normalized_offset = self._normalize_offset(offset)

        rows, total_count = self.repo.search(
            market=normalized_market,
            year=year,
            cash_min=cash_min,
            stock_min=stock_min,
            total_min=total_min,
            sort_by=normalized_sort_by,
            sort_dir=normalized_sort_dir,
            limit=normalized_limit,
            offset=normalized_offset,
        )

        items = self._to_response_items(rows)
        return items, total_count

    # --------------------------------------------------
    # internal helpers
    # --------------------------------------------------

    def _normalize_market(self, market: str | None) -> str | None:
        if market is None:
            return None

        text = str(market).strip().upper()
        if text not in self.VALID_MARKETS:
            raise ValueError("INVALID_MARKET")

        return text

    def _normalize_sort_by(self, sort_by: str | None) -> str:
        if sort_by is None:
            return "total"

        text = str(sort_by).strip().lower()
        if text not in self.VALID_SORT_BY:
            raise ValueError("INVALID_SORT_BY")

        return text

    def _normalize_sort_dir(self, sort_dir: str | None) -> str:
        if sort_dir is None:
            return "desc"

        text = str(sort_dir).strip().lower()
        if text not in self.VALID_SORT_DIR:
            raise ValueError("INVALID_SORT_DIR")

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

    def _to_response_items(self, rows: list):
        items: list[dict] = []

        for dividend, stock in rows:
            items.append(
                {
                    "stock_code": stock.stock_code,
                    "market": stock.market,
                    "company_name": stock.company_name,
                    "company_short_name": stock.company_short_name,
                    "industry": stock.industry,
                    "industry_name": get_industry_name(stock.industry),
                    "dividend_year": dividend.dividend_year,
                    "dividend_year_ad": get_ad_year(dividend.dividend_year),
                    "period_label": dividend.period_label,
                    "cash_dividend_per_share": dividend.cash_dividend_per_share,
                    "stock_dividend_per_share": dividend.stock_dividend_per_share,
                    "total_dividend_per_share": dividend.total_dividend_per_share,
                }
            )

        return items