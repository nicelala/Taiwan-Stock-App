from datetime import date
from decimal import Decimal

import pytest

from app.models.stock_basic import StockBasic
from app.models.refresh_job_log import RefreshJobLog
from app.services.stock_service import StockService
from app.services.dividend_service import DividendService


def test_stock_refresh_success_creates_job_log(db_session, monkeypatch):
    service = StockService(db_session)

    def fake_fetch_stock_rows(self, market):
        return [
            {
                "公司代號": "1101",
                "公司名稱": "台灣水泥股份有限公司",
                "公司簡稱": "台泥",
                "產業別": "01",
                "普通股每股面額": "10",
                "上市日期": "1962/02/09",
                "實收資本額": "77500000000",
                "已發行普通股數或TDR原股發行股數": "7750000000",
            }
        ]

    monkeypatch.setattr(StockService, "_fetch_stock_rows", fake_fetch_stock_rows)

    result = service.sync_from_source("TWSE")

    assert result["status"] == "success"
    assert result["market"] == "TWSE"
    assert result["count"] == 1

    log = db_session.query(RefreshJobLog).order_by(RefreshJobLog.id.desc()).first()
    assert log is not None
    assert log.job_name == "refresh_stocks"
    assert log.market == "TWSE"
    assert log.status == "success"
    assert log.inserted_or_updated_count == 1
    assert log.skipped_count == 0
    assert log.error_message is None
    assert log.duration_ms is not None
    assert log.trigger_source == "api"


def test_stock_refresh_invalid_market_creates_failed_job_log(db_session):
    service = StockService(db_session)

    with pytest.raises(ValueError, match="INVALID_MARKET"):
        service.sync_from_source("BAD")

    log = db_session.query(RefreshJobLog).order_by(RefreshJobLog.id.desc()).first()
    assert log is not None
    assert log.job_name == "refresh_stocks"
    assert log.market == "BAD"
    assert log.status == "failed"
    assert log.error_message is not None
    assert "INVALID_MARKET" in log.error_message
    assert log.duration_ms is not None


def test_dividend_refresh_success_creates_job_log(db_session):
    stock = StockBasic(
        stock_code="2330",
        market="TWSE",
        company_name="台灣積體電路製造股份有限公司",
        company_short_name="台積電",
        industry="24",
        par_value=Decimal("10.0000"),
        listing_date=date(1994, 9, 5),
        capital_amount=100,
        issued_common_shares=10,
        source_name="TEST",
        source_url="https://example.test/stock",
    )
    db_session.add(stock)
    db_session.commit()
    db_session.refresh(stock)

    service = DividendService(db_session)

    def fake_fetch_dividend_rows(self, market):
        return [
            {
                "公司代號": "2330",
                "股利年度": "114",
                "期別": "1",
                "決議進度": "董事會決議",
                "董事會決議日": "2026/02/10",
                "現金股利(元/股)": "6.0",
                "股票股利(元/股)": "0.0",
            }
        ]

    # 綁到 instance method 的 class level
    DividendService._fetch_dividend_rows = fake_fetch_dividend_rows

    result = service.sync_from_source("TWSE")

    assert result["status"] == "success"
    assert result["market"] == "TWSE"
    assert result["count"] == 1
    assert result["skipped"] == 0

    log = db_session.query(RefreshJobLog).order_by(RefreshJobLog.id.desc()).first()
    assert log is not None
    assert log.job_name == "refresh_dividends"
    assert log.market == "TWSE"
    assert log.status == "success"
    assert log.inserted_or_updated_count == 1
    assert log.skipped_count == 0
    assert log.error_message is None
    assert log.duration_ms is not None
    assert log.trigger_source == "api"