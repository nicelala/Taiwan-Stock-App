from __future__ import annotations

from decimal import Decimal
from sqlalchemy.orm import Session

from app.crawlers.twse_client import TWSEClient
from app.crawlers.tpex_client import TPExClient
from app.core.utils import parse_date, parse_decimal, fix_mojibake, get_first
from app.repositories.stock_repository import StockRepository


class StockService:
    VALID_MARKETS = {"TWSE", "TPEX"}

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = StockRepository(db)
        self.twse_client = TWSEClient()
        self.tpex_client = TPExClient()

    def get_stock(self, stock_code: str, market: str | None = None):
        """
        market 指定時：只查單一市場
        market=None 時：
            - 若只找到一筆，直接回傳
            - 若找到多筆（跨市場重碼），拋 ValueError
            - 若找不到，回 None
        """
        if market is not None:
            market = market.upper()
            self._validate_market(market)
            return self.repo.get_by_code(stock_code, market)

        matches = self.repo.list_by_code(stock_code)

        if len(matches) == 1:
            return matches[0]

        if len(matches) > 1:
            raise ValueError("MULTIPLE_MARKET_MATCH")

        return None

    def sync_from_source(self, market: str) -> dict:
        market = market.upper()
        self._validate_market(market)

        rows = self._fetch_stock_rows(market)
        inserted_or_updated = 0

        for raw in rows:
            payload = self._normalize_stock_row(raw, market)
            if payload["stock_code"] is None:
                continue

            self.repo.upsert_one(payload)
            inserted_or_updated += 1

        self.db.commit()

        return {
            "status": "success",
            "market": market,
            "count": inserted_or_updated,
        }

    def sync_one_if_missing(self, stock_code: str, market: str | None = None):
        """
        單一股票查無資料時，自動 refresh 再查
        """
        if market is not None:
            market = market.upper()
            self._validate_market(market)

            obj = self.repo.get_by_code(stock_code, market)
            if obj:
                return obj

            self.sync_from_source(market)
            return self.repo.get_by_code(stock_code, market)

        # market 未指定：先看 local DB 是否已有單一明確結果
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

    def _fetch_stock_rows(self, market: str) -> list[dict]:
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
