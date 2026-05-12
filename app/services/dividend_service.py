from __future__ import annotations

from decimal import Decimal
from sqlalchemy.orm import Session

from app.crawlers.twse_client import TWSEClient
from app.crawlers.tpex_client import TPExClient
from app.core.utils import (
    parse_date,
    parse_decimal,
    split_code_and_name,
    get_first,
    fix_mojibake,
    get_ad_year,
)
from app.repositories.dividend_repository import DividendRepository
from app.repositories.stock_repository import StockRepository
from app.repositories.refresh_job_log_repository import RefreshJobLogRepository
from app.services.stock_service import StockService


class DividendService:
    VALID_MARKETS = {"TWSE", "TPEX"}

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = DividendRepository(db)
        self.stock_repo = StockRepository(db)
        self.log_repo = RefreshJobLogRepository(db)
        self.stock_service = StockService(db)
        self.twse_client = TWSEClient()
        self.tpex_client = TPExClient()

    def list_dividends(
        self,
        stock_code: str,
        market: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
    ):
        resolved_market = self._resolve_market(stock_code, market)
        rows = self.repo.list_by_stock_code(stock_code, resolved_market, year_from, year_to)
        return self._attach_derived_fields_list(rows)

    def sync_from_source(self, market: str, trigger_source: str = "api") -> dict:
        market_text = str(market or "").strip().upper()
        log = self.log_repo.create_running(
            job_name="refresh_dividends",
            market=market_text or "UNKNOWN",
            trigger_source=trigger_source,
        )

        try:
            self._validate_market(market_text)

            rows = self._fetch_dividend_rows(market_text)
            inserted_or_updated = 0
            skipped = 0

            for raw in rows:
                normalized = self._normalize_dividend_row(raw, market_text)
                if normalized is None:
                    skipped += 1
                    continue

                stock = self.stock_repo.get_by_code(normalized["stock_code"], market_text)
                if stock is None:
                    skipped += 1
                    continue

                normalized["stock_id"] = stock.id
                self.repo.upsert_one(normalized)
                inserted_or_updated += 1

            self.db.commit()

            self.log_repo.mark_success(
                log_id=log.id,
                inserted_or_updated_count=inserted_or_updated,
                skipped_count=skipped,
            )

            return {
                "status": "success",
                "market": market_text,
                "count": inserted_or_updated,
                "skipped": skipped,
            }

        except Exception as exc:
            self.db.rollback()
            self.log_repo.mark_failed(log.id, str(exc))
            raise

    def sync_one_if_missing(self, stock_code: str, market: str | None = None):
        resolved_market = self._resolve_market(stock_code, market, allow_missing=True)

        rows = self.repo.list_by_stock_code(stock_code, resolved_market)
        if rows:
            return self._attach_derived_fields_list(rows)

        # 若股票基本資料尚未存在，先補股票基本資料
        stock = self.stock_repo.get_by_code(stock_code, resolved_market)
        if stock is None:
            self.stock_service.sync_from_source(resolved_market)

        self.sync_from_source(resolved_market)
        rows = self.repo.list_by_stock_code(stock_code, resolved_market)
        return self._attach_derived_fields_list(rows)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_market(self, market: str) -> None:
        if market not in self.VALID_MARKETS:
            raise ValueError("INVALID_MARKET")

    def _resolve_market(
        self,
        stock_code: str,
        market: str | None,
        allow_missing: bool = False,
    ) -> str:
        if market is not None:
            market = market.upper()
            self._validate_market(market)
            return market

        stock = self.stock_service.get_stock(stock_code, None)
        if stock is not None:
            return stock.market

        if allow_missing:
            # 若本地還沒有任何股票資料，先預設依序 refresh 時由 route/service 再處理
            # 這裡維持與 stock service 同步策略：先 TWSE 再 TPEX
            return "TWSE"

        raise ValueError("STOCK_NOT_FOUND")

    def _fetch_dividend_rows(self, market: str) -> list:
        if market == "TWSE":
            return self.twse_client.fetch_dividend_all()
        if market == "TPEX":
            return self.tpex_client.fetch_dividend_all()
        raise ValueError("INVALID_MARKET")

    def _normalize_dividend_row(self, raw: dict, market: str) -> dict | None:
        raw_code_name = get_first(raw, "公司代號名稱", "公司代號及名稱")
        stock_code_from_combined, _company_name_from_combined = split_code_and_name(raw_code_name)

        stock_code = str(get_first(raw, "公司代號") or "").strip() or stock_code_from_combined
        if not stock_code:
            return None

        dividend_year_raw = get_first(raw, "股利年度")
        try:
            dividend_year = int(str(dividend_year_raw).strip())
        except Exception:
            return None

        period_label = str(get_first(raw, "期別") or "").strip() or None

        resolution_status = fix_mojibake(
            get_first(raw, "決議（擬議）進度", "決議進度", "決議狀態")
        )
        resolution_status = resolution_status.strip() if resolution_status else None

        board_approved_date = parse_date(
            get_first(
                raw,
                "董事會（擬議）股利分派日",
                "董事會決議通過股利分派日",
                "董事會決議日",
            )
        )
        shareholder_meeting_date = parse_date(get_first(raw, "股東會日期"))

        cash_earnings = parse_decimal(get_first(
            raw,
            "股東配發內容-盈餘分配之現金股利 (元/股)",
            "股東配發內容-盈餘分配之現金股利(元/股)",
            "股東配發-盈餘分配之現金股利 (元/股)",
            "股東配發-盈餘分配之現金股利(元/股)",
            "現金股利(元/股)",
            "現金股利 (元/股)",
        )) or Decimal("0")

        cash_other_combined = parse_decimal(get_first(
            raw,
            "股東配發內容-法定盈餘公積、資本公積發放之現金 (元/股)",
            "股東配發內容-法定盈餘公積、資本公積發放之現金(元/股)",
            "股東配發-法定盈餘公積、資本公積發放之現金 (元/股)",
            "股東配發-法定盈餘公積、資本公積發放之現金(元/股)",
        )) or Decimal("0")

        cash_legal = parse_decimal(get_first(
            raw,
            "股東配發-法定盈餘公積發放之現金 (元/股)",
            "股東配發-法定盈餘公積發放之現金(元/股)",
        )) or Decimal("0")

        cash_capital = parse_decimal(get_first(
            raw,
            "股東配發-資本公積發放之現金 (元/股)",
            "股東配發-資本公積發放之現金(元/股)",
        )) or Decimal("0")

        stock_earnings = parse_decimal(get_first(
            raw,
            "股東配發內容-盈餘轉增資配股 (元/股)",
            "股東配發內容-盈餘轉增資配股(元/股)",
            "股東配發-盈餘轉增資配股 (元/股)",
            "股東配發-盈餘轉增資配股(元/股)",
            "股票股利(元/股)",
            "股票股利 (元/股)",
        )) or Decimal("0")

        stock_other_combined = parse_decimal(get_first(
            raw,
            "股東配發內容-法定盈餘公積、資本公積轉增資配股 (元/股)",
            "股東配發內容-法定盈餘公積、資本公積轉增資配股(元/股)",
            "股東配發-法定盈餘公積、資本公積轉增資配股 (元/股)",
            "股東配發-法定盈餘公積、資本公積轉增資配股(元/股)",
        )) or Decimal("0")

        stock_legal = parse_decimal(get_first(
            raw,
            "股東配發-法定盈餘公積轉增資配股 (元/股)",
            "股東配發-法定盈餘公積轉增資配股(元/股)",
        )) or Decimal("0")

        stock_capital = parse_decimal(get_first(
            raw,
            "股東配發-資本公積轉增資配股 (元/股)",
            "股東配發-資本公積轉增資配股(元/股)",
        )) or Decimal("0")

        cash_dividend_per_share = cash_earnings + cash_other_combined + cash_legal + cash_capital
        stock_dividend_per_share = stock_earnings + stock_other_combined + stock_legal + stock_capital
        total_dividend_per_share = cash_dividend_per_share + stock_dividend_per_share

        par_value = parse_decimal(get_first(raw, "普通股每股面額"))

        stock_dividend_rate_pct = None
        if par_value and par_value != 0:
            stock_dividend_rate_pct = (stock_dividend_per_share / par_value) * Decimal("100")

        belongs_to_year_or_period = (
            str(get_first(raw, "股利所屬年 (季)度", "股利所屬年度") or "").strip()
            or None
        )

        source_url = (
            "https://openapi.twse.com.tw/v1/opendata/t187ap45_L"
            if market == "TWSE"
            else "https://mopsfin.twse.com.tw/opendata/t187ap45_O.csv"
        )

        biz_key = "|".join([
            stock_code,
            market,
            str(dividend_year),
            period_label or "",
            board_approved_date.isoformat() if board_approved_date else "",
            resolution_status or "",
        ])

        return {
            "stock_code": stock_code,
            "market": market,
            "dividend_year": dividend_year,
            "belongs_to_year_or_period": belongs_to_year_or_period,
            "period_label": period_label,
            "resolution_status": resolution_status,
            "board_approved_date": board_approved_date,
            "shareholder_meeting_date": shareholder_meeting_date,
            "cash_dividend_per_share": cash_dividend_per_share,
            "stock_dividend_per_share": stock_dividend_per_share,
            "total_dividend_per_share": total_dividend_per_share,
            "stock_dividend_rate_pct": stock_dividend_rate_pct,
            "par_value": par_value,
            "source_name": f"{market}_OPEN_DATA",
            "source_url": source_url,
            "biz_key": biz_key,
        }

    def _attach_derived_fields(self, obj):
        """
        不改 DB schema，僅在回傳 ORM 物件前補上衍生欄位。
        """
        if obj is None:
            return None

        obj.dividend_year_ad = get_ad_year(obj.dividend_year)
        return obj

    def _attach_derived_fields_list(self, rows: list):
        return [self._attach_derived_fields(row) for row in rows]