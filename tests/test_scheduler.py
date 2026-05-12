from datetime import date
from decimal import Decimal

from app.models.stock_basic import StockBasic
from app.models.refresh_job_log import RefreshJobLog
from app.scheduler import run_refresh_stocks_job, run_refresh_dividends_job
from app.services.stock_service import StockService
from app.services.dividend_service import DividendService


def test_run_refresh_stocks_job_creates_scheduler_log(db_session, monkeypatch):
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

    run_refresh_stocks_job("TWSE")

    db_session.expire_all()
    log = db_session.query(RefreshJobLog).order_by(RefreshJobLog.id.desc()).first()

    assert log is not None
    assert log.job_name == "refresh_stocks"
    assert log.market == "TWSE"
    assert log.status == "success"
    assert log.trigger_source == "scheduler"


def test_run_refresh_dividends_job_creates_scheduler_log(db_session, monkeypatch):
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

    def fake_fetch_stock_rows(self, market):
        return [
            {
                "公司代號": "2330",
                "公司名稱": "台灣積體電路製造股份有限公司",
                "公司簡稱": "台積電",
                "產業別": "24",
                "普通股每股面額": "10",
                "上市日期": "1994/09/05",
                "實收資本額": "100",
                "已發行普通股數或TDR原股發行股數": "10",
            }
        ]

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

    monkeypatch.setattr(StockService, "_fetch_stock_rows", fake_fetch_stock_rows)
    monkeypatch.setattr(DividendService, "_fetch_dividend_rows", fake_fetch_dividend_rows)

    run_refresh_dividends_job("TWSE")

    db_session.expire_all()
    logs = (
        db_session.query(RefreshJobLog)
        .order_by(RefreshJobLog.id.desc())
        .all()
    )

    assert len(logs) >= 2

    latest = logs[0]
    assert latest.job_name == "refresh_dividends"
    assert latest.market == "TWSE"
    assert latest.status == "success"
    assert latest.trigger_source == "scheduler"