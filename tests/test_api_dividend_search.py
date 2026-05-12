from datetime import date
from decimal import Decimal

from app.models.stock_basic import StockBasic
from app.models.dividend_history import DividendHistory


def _seed_dividend_search_data(db_session):
    stock_2330 = StockBasic(
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
        source_url="https://example.test/2330",
    )
    stock_6488 = StockBasic(
        stock_code="6488",
        market="TPEX",
        company_name="環球晶圓股份有限公司",
        company_short_name="環球晶",
        industry="24",
        par_value=Decimal("10.0000"),
        listing_date=date(2015, 9, 25),
        capital_amount=100,
        issued_common_shares=10,
        source_name="TEST",
        source_url="https://example.test/6488",
    )
    stock_1101 = StockBasic(
        stock_code="1101",
        market="TWSE",
        company_name="台灣水泥股份有限公司",
        company_short_name="台泥",
        industry="01",
        par_value=Decimal("10.0000"),
        listing_date=date(1962, 2, 9),
        capital_amount=100,
        issued_common_shares=10,
        source_name="TEST",
        source_url="https://example.test/1101",
    )

    db_session.add_all([stock_2330, stock_6488, stock_1101])
    db_session.commit()
    db_session.refresh(stock_2330)
    db_session.refresh(stock_6488)
    db_session.refresh(stock_1101)

    rows = [
        DividendHistory(
            stock_id=stock_2330.id,
            stock_code="2330",
            market="TWSE",
            dividend_year=114,
            belongs_to_year_or_period="114",
            period_label="1",
            resolution_status="董事會決議",
            board_approved_date=date(2026, 2, 10),
            shareholder_meeting_date=None,
            cash_dividend_per_share=Decimal("6.0000"),
            stock_dividend_per_share=Decimal("0.0000"),
            total_dividend_per_share=Decimal("6.0000"),
            stock_dividend_rate_pct=None,
            par_value=None,
            source_name="TEST",
            source_url="https://example.test/dividend/2330",
            biz_key="2330|TWSE|114|1|2026-02-10|董事會決議",
        ),
        DividendHistory(
            stock_id=stock_6488.id,
            stock_code="6488",
            market="TPEX",
            dividend_year=114,
            belongs_to_year_or_period="114",
            period_label="1",
            resolution_status="董事會決議",
            board_approved_date=date(2026, 3, 3),
            shareholder_meeting_date=None,
            cash_dividend_per_share=Decimal("5.7000"),
            stock_dividend_per_share=Decimal("0.0000"),
            total_dividend_per_share=Decimal("5.7000"),
            stock_dividend_rate_pct=None,
            par_value=None,
            source_name="TEST",
            source_url="https://example.test/dividend/6488",
            biz_key="6488|TPEX|114|1|2026-03-03|董事會決議",
        ),
        DividendHistory(
            stock_id=stock_1101.id,
            stock_code="1101",
            market="TWSE",
            dividend_year=113,
            belongs_to_year_or_period="113",
            period_label="1",
            resolution_status="董事會決議",
            board_approved_date=date(2025, 2, 15),
            shareholder_meeting_date=None,
            cash_dividend_per_share=Decimal("1.2000"),
            stock_dividend_per_share=Decimal("0.0000"),
            total_dividend_per_share=Decimal("1.2000"),
            stock_dividend_rate_pct=None,
            par_value=None,
            source_name="TEST",
            source_url="https://example.test/dividend/1101",
            biz_key="1101|TWSE|113|1|2025-02-15|董事會決議",
        ),
    ]

    db_session.add_all(rows)
    db_session.commit()


def test_search_dividends_by_year(client, db_session):
    _seed_dividend_search_data(db_session)

    resp = client.get("/api/v1/dividends/search?year=114")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 2
    assert data["total_count"] == 2
    assert all(item["dividend_year"] == 114 for item in data["items"])


def test_search_dividends_by_market(client, db_session):
    _seed_dividend_search_data(db_session)

    resp = client.get("/api/v1/dividends/search?market=TPEX")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["total_count"] == 1
    assert data["items"][0]["market"] == "TPEX"
    assert data["items"][0]["stock_code"] == "6488"


def test_search_dividends_by_cash_min(client, db_session):
    _seed_dividend_search_data(db_session)

    resp = client.get("/api/v1/dividends/search?cash_min=5")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 2
    assert data["total_count"] == 2
    assert all(Decimal(item["cash_dividend_per_share"]) >= Decimal("5") for item in data["items"])


def test_search_dividends_by_total_min(client, db_session):
    _seed_dividend_search_data(db_session)

    resp = client.get("/api/v1/dividends/search?total_min=6")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["total_count"] == 1
    assert data["items"][0]["stock_code"] == "2330"
    assert Decimal(data["items"][0]["total_dividend_per_share"]) >= Decimal("6")


def test_search_dividends_sort_by_cash_desc(client, db_session):
    _seed_dividend_search_data(db_session)

    resp = client.get("/api/v1/dividends/search?sort_by=cash&sort_dir=desc")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 3
    assert data["total_count"] == 3

    first = Decimal(data["items"][0]["cash_dividend_per_share"])
    second = Decimal(data["items"][1]["cash_dividend_per_share"])
    assert first >= second


def test_search_dividends_includes_industry_name_and_dividend_year_ad(client, db_session):
    _seed_dividend_search_data(db_session)

    resp = client.get("/api/v1/dividends/search?market=TWSE&year=114")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["total_count"] == 1

    item = data["items"][0]
    assert item["industry"] == "24"
    assert item["industry_name"] == "半導體業"
    assert item["dividend_year"] == 114
    assert item["dividend_year_ad"] == 2025


def test_search_dividends_limit_and_offset(client, db_session):
    _seed_dividend_search_data(db_session)

    resp = client.get("/api/v1/dividends/search?limit=1&offset=1")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["total_count"] == 3
    assert len(data["items"]) == 1


def test_search_dividends_invalid_market_returns_422(client):
    resp = client.get("/api/v1/dividends/search?market=BAD")
    assert resp.status_code == 422

    data = resp.json()
    assert data["detail"]["code"] == "INVALID_MARKET"


def test_search_dividends_invalid_sort_by_returns_422(client):
    resp = client.get("/api/v1/dividends/search?sort_by=BAD")
    assert resp.status_code == 422

    data = resp.json()
    assert data["detail"]["code"] == "INVALID_SORT_BY"


def test_search_dividends_invalid_sort_dir_returns_422(client):
    resp = client.get("/api/v1/dividends/search?sort_dir=BAD")
    assert resp.status_code == 422

    data = resp.json()
    assert data["detail"]["code"] == "INVALID_SORT_DIR"