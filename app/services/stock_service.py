from __future__ import annotations

from decimal import Decimal
from sqlalchemy.orm import Session

from app.crawlers.twse_client import TWSEClient
from app.crawlers.tpex_client import TPExClient
from app.core.utils import (
    parse_date,
    parse_decimal,
    fix_mojibake,
    get_first,
    get_industry_name,
)
from app.repositories.stock_repository import StockRepository
from app.repositories.refresh_job_log_repository import RefreshJobLogRepository


class StockService:
    VALID_MARKETS = {"TWSE", "TPEX"}

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = StockRepository(db)
        self.log_repo = RefreshJobLogRepository(db)
        self.twse_client = TWSEClient()
        self.tpex_client = TPExClient()

    
    
    def get_stock(self, stock_code: str, market: str | None = None):
        normalized_market = self._normalize_market(market)
        result = self.repo.get_by_code(stock_code=stock_code, market=normalized_market)

        if normalized_market is not None:
            return result

        if isinstance(result, list):
            if len(result) == 0:
                return None
            if len(result) == 1:
                return result[0]
            raise ValueError("MULTIPLE_MARKET_MATCH")

        return result

    def search(
        self,
        q: str,
        market: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ):
        normalized_market = self._normalize_market(market)
        normalized_limit = self._normalize_limit(limit)
        normalized_offset = self._normalize_offset(offset)

        rows, total_count = self.repo.search(
            q=q,
            market=normalized_market,
            limit=normalized_limit,
            offset=normalized_offset,
        )

        items = []
        for stock in rows:
            items.append(
                {
                    "stock_code": stock.stock_code,
                    "market": stock.market,
                    "company_name": stock.company_name,
                    "company_short_name": stock.company_short_name,
                    "industry": stock.industry,
                    "industry_name": get_industry_name(stock.industry),
                    "listing_date": stock.listing_date,
                }
            )

        return items, total_count

    def sync_from_source(self, market: str, trigger_source: str = "api") -> dict:
        market_text = str(market or "").strip().upper()
        log = self.log_repo.create_running(
            job_name="refresh_stocks",
            market=market_text or "UNKNOWN",
            trigger_source=trigger_source,
        )

        try:
            self._validate_market(market_text)

            rows = self._fetch_stock_rows(market_text)
            inserted_or_updated = 0

            for raw in rows:
                payload = self._normalize_stock_row(raw, market_text)
                if payload["stock_code"] is None:
                    continue

                self.repo.upsert_one(payload)
                inserted_or_updated += 1

            self.db.commit()

            self.log_repo.mark_success(
                log_id=log.id,
                inserted_or_updated_count=inserted_or_updated,
                skipped_count=0,
            )

            return {
                "status": "success",
                "market": market_text,
                "count": inserted_or_updated,
            }

        except Exception as exc:
            self.db.rollback()
            self.log_repo.mark_failed(log.id, str(exc))
            raise

    def sync_one_if_missing(self, stock_code: str, market: str | None = None):
        """
        單一股票查無資料時，自動 refresh 再查
        """
        if market is not None:
            market = market.upper()
            self._validate_market(market)

            obj = self.repo.get_by_code(stock_code, market)
            if obj:
                return self._attach_derived_fields(obj)

            self.sync_from_source(market)
            obj = self.repo.get_by_code(stock_code, market)
            return self._attach_derived_fields(obj)

        obj = self.get_stock(stock_code, None)
        if obj:
            return obj

        # 依序 refresh TWSE -> TPEX
        self.sync_from_source("TWSE")
        obj = self.get_stock(stock_code, None)
        if obj:
            return obj

        self.sync_from_source("TPEX")
        return self.get_stock(stock_code, None)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_market(self, market: str) -> None:
        if market not in self.VALID_MARKETS:
            raise ValueError("INVALID_MARKET")

    def _fetch_stock_rows(self, market: str) -> list:
        if market == "TWSE":
            return self.twse_client.fetch_stock_basic_all()
        if market == "TPEX":
            return self.tpex_client.fetch_stock_basic_all()
        raise ValueError("INVALID_MARKET")

    def _normalize_stock_row(self, raw: dict, market: str) -> dict:
        stock_code = str(get_first(raw, "公司代號") or "").strip() or None

        company_name = fix_mojibake(get_first(raw, "公司名稱")) or ""
        company_short_name = fix_mojibake(get_first(raw, "公司簡稱"))

        industry = str(get_first(raw, "產業別") or "").strip() or None

        par_value = parse_decimal(get_first(raw, "普通股每股面額"))
        listing_date = parse_date(get_first(raw, "上市日期", "上櫃日期"))

        capital_amount = parse_decimal(get_first(raw, "實收資本額"))
        issued_common_shares = parse_decimal(
            get_first(raw, "已發行普通股數或TDR原股發行股數")
        )

        source_url = (
            "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
            if market == "TWSE"
            else "https://mopsfin.twse.com.tw/opendata/t187ap03_O.csv"
        )

        return {
            "stock_code": stock_code,
            "market": market,
            "company_name": company_name,
            "company_short_name": company_short_name,
            "industry": industry,
            "par_value": par_value,
            "listing_date": listing_date,
            "capital_amount": int(capital_amount) if isinstance(capital_amount, Decimal) else None,
            "issued_common_shares": int(issued_common_shares) if isinstance(issued_common_shares, Decimal) else None,
            "source_name": f"{market}_OPEN_DATA",
            "source_url": source_url,
        }

    def _attach_derived_fields(self, obj):
        """
        不改 DB schema，僅在回傳 ORM 物件前補上衍生欄位。
        """
        if obj is None:
            return None

        obj.industry_name = get_industry_name(obj.industry)
        return obj
    
    
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

