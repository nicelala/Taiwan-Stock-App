from decimal import Decimal
from datetime import date

from app.models.stock_basic import StockBasic
from app.models.dividend_history import DividendHistory


def test_get_stock_basic_success(client, seed_stock_basic):
    resp = client.get("/api/v1/stocks/2330")
    assert resp.status_code == 200

    data = resp.json()
    assert data["stock_code"] == "2330"
    assert data["market"] == "TWSE"
    assert data["company_name"] == "台灣積體電路製造股份有限公司"
    assert data["company_short_name"] == "台積電"
    assert data["industry"] == "24"
    assert data["industry_name"] == "半導體業"


def test_get_stock_basic_not_found(client):
    resp = client.get("/api/v1/stocks/9999")
    assert resp.status_code == 404

    data = resp.json()
    assert data["detail"]["code"] == "STOCK_NOT_FOUND"


def test_get_dividends_success(client, seed_dividends):
    resp = client.get("/api/v1/stocks/2330/dividends")
    assert resp.status_code == 200

    data = resp.json()
    assert data["stock_code"] == "2330"
    assert data["market"] == "TWSE"
    assert len(data["items"]) == 2

    assert data["items"][0]["dividend_year"] == 114
    assert data["items"][0]["dividend_year_ad"] == 2025
    assert data["items"][0]["cash_dividend_per_share"] == "6.0000"


def test_get_dividends_filter_by_year(client, seed_dividends):
    resp = client.get("/api/v1/stocks/2330/dividends?year_from=114&year_to=114")
    assert resp.status_code == 200

    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["dividend_year"] == 114
    assert data["items"][0]["dividend_year_ad"] == 2025


def test_get_dividends_invalid_year_range(client, seed_dividends):
    resp = client.get("/api/v1/stocks/2330/dividends?year_from=115&year_to=114")
    assert resp.status_code == 422

    data = resp.json()
    assert data["detail"]["code"] == "INVALID_YEAR_RANGE"


# -----------------------------
# 第 2-1 批：TPEX stock API
# -----------------------------

def test_get_stock_basic_success_tpex_with_market(client, db_session):
    stock = StockBasic(
        stock_code="6488",
        market="TPEX",
        company_name="環球晶圓股份有限公司",
        company_short_name="環球晶",
        industry="24",
        par_value=Decimal("10.0000"),
        listing_date=date(2015, 9, 25),
        capital_amount=4781137250,
        issued_common_shares=478113725,
        source_name="TEST",
        source_url="https://example.test/tpex-stock",
    )
    db_session.add(stock)
    db_session.commit()

    resp = client.get("/api/v1/stocks/6488?market=TPEX")
    assert resp.status_code == 200

    data = resp.json()
    assert data["stock_code"] == "6488"
    assert data["market"] == "TPEX"
    assert data["company_name"] == "環球晶圓股份有限公司"
    assert data["company_short_name"] == "環球晶"
    assert data["industry"] == "24"
    assert data["industry_name"] == "半導體業"


def test_get_stock_basic_fallback_to_tpex_when_only_tpex_exists(client, db_session):
    stock = StockBasic(
        stock_code="6488",
        market="TPEX",
        company_name="環球晶圓股份有限公司",
        company_short_name="環球晶",
        industry="24",
        par_value=Decimal("10.0000"),
        listing_date=date(2015, 9, 25),
        capital_amount=4781137250,
        issued_common_shares=478113725,
        source_name="TEST",
        source_url="https://example.test/tpex-stock",
    )
    db_session.add(stock)
    db_session.commit()

    resp = client.get("/api/v1/stocks/6488")
    assert resp.status_code == 200

    data = resp.json()
    assert data["stock_code"] == "6488"
    assert data["market"] == "TPEX"
    assert data["industry"] == "24"
    assert data["industry_name"] == "半導體業"


def test_get_stock_basic_multiple_market_match_returns_409(client, db_session):
    db_session.add_all(
        [
            StockBasic(
                stock_code="9999",
                market="TWSE",
                company_name="測試上市公司",
                company_short_name="上市測試",
                industry="24",
                par_value=Decimal("10.0000"),
                listing_date=date(2020, 1, 1),
                capital_amount=100,
                issued_common_shares=10,
                source_name="TEST",
                source_url="https://example.test/twse",
            ),
            StockBasic(
                stock_code="9999",
                market="TPEX",
                company_name="測試上櫃公司",
                company_short_name="上櫃測試",
                industry="24",
                par_value=Decimal("10.0000"),
                listing_date=date(2020, 1, 1),
                capital_amount=100,
                issued_common_shares=10,
                source_name="TEST",
                source_url="https://example.test/tpex",
            ),
        ]
    )
    db_session.commit()

    resp = client.get("/api/v1/stocks/9999")
    assert resp.status_code == 409

    data = resp.json()
    assert data["detail"]["code"] == "MULTIPLE_MARKET_MATCH"


def test_refresh_stocks_invalid_market_returns_422(client):
    resp = client.post("/api/v1/admin/refresh/stocks?market=INVALID")
    assert resp.status_code == 422

    data = resp.json()
    assert data["detail"]["code"] == "INVALID_MARKET"


# -----------------------------
# 第 2-2 批新增：TPEX dividend API
# -----------------------------

def test_get_dividends_success_tpex_with_market(client, db_session):
    stock = StockBasic(
        stock_code="6488",
        market="TPEX",
        company_name="環球晶圓股份有限公司",
        company_short_name="環球晶",
        industry="24",
        par_value=Decimal("10.0000"),
        listing_date=date(2015, 9, 25),
        capital_amount=4781137250,
        issued_common_shares=478113725,
        source_name="TEST",
        source_url="https://example.test/tpex-stock",
    )
    db_session.add(stock)
    db_session.commit()
    db_session.refresh(stock)

    item = DividendHistory(
        stock_id=stock.id,
        stock_code="6488",
        market="TPEX",
        dividend_year=114,
        belongs_to_year_or_period="114",
        period_label="1",
        resolution_status="董事會決議",
        board_approved_date=date(2026, 3, 1),
        shareholder_meeting_date=None,
        cash_dividend_per_share=Decimal("8.0000"),
        stock_dividend_per_share=Decimal("0.0000"),
        total_dividend_per_share=Decimal("8.0000"),
        stock_dividend_rate_pct=None,
        par_value=None,
        source_name="TEST",
        source_url="https://example.test/tpex-dividend",
        biz_key="6488|TPEX|114|1|2026-03-01|董事會決議",
    )
    db_session.add(item)
    db_session.commit()

    resp = client.get("/api/v1/stocks/6488/dividends?market=TPEX")
    assert resp.status_code == 200

    data = resp.json()
    assert data["stock_code"] == "6488"
    assert data["market"] == "TPEX"
    assert len(data["items"]) == 1
    assert data["items"][0]["dividend_year"] == 114
    assert data["items"][0]["dividend_year_ad"] == 2025
    assert data["items"][0]["cash_dividend_per_share"] == "8.0000"


def test_get_dividends_fallback_to_tpex_when_only_tpex_exists(client, db_session):
    stock = StockBasic(
        stock_code="6488",
        market="TPEX",
        company_name="環球晶圓股份有限公司",
        company_short_name="環球晶",
        industry="24",
        par_value=Decimal("10.0000"),
        listing_date=date(2015, 9, 25),
        capital_amount=4781137250,
        issued_common_shares=478113725,
        source_name="TEST",
        source_url="https://example.test/tpex-stock",
    )
    db_session.add(stock)
    db_session.commit()
    db_session.refresh(stock)

    item = DividendHistory(
        stock_id=stock.id,
        stock_code="6488",
        market="TPEX",
        dividend_year=114,
        belongs_to_year_or_period="114",
        period_label="1",
        resolution_status="董事會決議",
        board_approved_date=date(2026, 3, 1),
        shareholder_meeting_date=None,
        cash_dividend_per_share=Decimal("8.0000"),
        stock_dividend_per_share=Decimal("0.0000"),
        total_dividend_per_share=Decimal("8.0000"),
        stock_dividend_rate_pct=None,
        par_value=None,
        source_name="TEST",
        source_url="https://example.test/tpex-dividend",
        biz_key="6488|TPEX|114|1|2026-03-01|董事會決議",
    )
    db_session.add(item)
    db_session.commit()

    resp = client.get("/api/v1/stocks/6488/dividends")
    assert resp.status_code == 200

    data = resp.json()
    assert data["market"] == "TPEX"
    assert len(data["items"]) == 1
    assert data["items"][0]["dividend_year_ad"] == 2025


def test_get_dividends_multiple_market_match_returns_409(client, db_session):
    db_session.add_all(
        [
            StockBasic(
                stock_code="7777",
                market="TWSE",
                company_name="測試上市公司",
                company_short_name="上市測試",
                industry="24",
                par_value=Decimal("10.0000"),
                listing_date=date(2020, 1, 1),
                capital_amount=100,
                issued_common_shares=10,
                source_name="TEST",
                source_url="https://example.test/twse",
            ),
            StockBasic(
                stock_code="7777",
                market="TPEX",
                company_name="測試上櫃公司",
                company_short_name="上櫃測試",
                industry="24",
                par_value=Decimal("10.0000"),
                listing_date=date(2020, 1, 1),
                capital_amount=100,
                issued_common_shares=10,
                source_name="TEST",
                source_url="https://example.test/tpex",
            ),
        ]
    )
    db_session.commit()

    resp = client.get("/api/v1/stocks/7777/dividends")
    assert resp.status_code == 409

    data = resp.json()
    assert data["detail"]["code"] == "MULTIPLE_MARKET_MATCH"


def test_refresh_dividends_invalid_market_returns_422(client):
    resp = client.post("/api/v1/admin/refresh/dividends?market=INVALID")
    assert resp.status_code == 422

    data = resp.json()
    assert data["detail"]["code"] == "INVALID_MARKET"


# -----------------------------
# v0.3.1-1 新增：industry_name
# -----------------------------

def test_get_stock_basic_unknown_industry_code_returns_null_industry_name(client, db_session):
    stock = StockBasic(
        stock_code="5555",
        market="TWSE",
        company_name="未知產業測試公司",
        company_short_name="未知產業",
        industry="999",
        par_value=Decimal("10.0000"),
        listing_date=date(2024, 1, 1),
        capital_amount=100,
        issued_common_shares=10,
        source_name="TEST",
        source_url="https://example.test/unknown-industry",
    )
    db_session.add(stock)
    db_session.commit()

    resp = client.get("/api/v1/stocks/5555?market=TWSE")
    assert resp.status_code == 200

    data = resp.json()
    assert data["industry"] == "999"
    assert data["industry_name"] is None