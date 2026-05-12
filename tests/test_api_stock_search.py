from decimal import Decimal
from datetime import date

from app.models.stock_basic import StockBasic


def test_search_stocks_by_stock_code_prefix(client, db_session):
    db_session.add_all(
        [
            StockBasic(
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
            ),
            StockBasic(
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
            ),
        ]
    )
    db_session.commit()

    resp = client.get("/api/v1/stocks/search?q=23")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["items"][0]["stock_code"] == "2330"
    assert data["items"][0]["industry_name"] == "半導體業"


def test_search_stocks_by_company_name(client, db_session):
    db_session.add(
        StockBasic(
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
    )
    db_session.commit()

    resp = client.get("/api/v1/stocks/search?q=台灣積體")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["items"][0]["stock_code"] == "2330"


def test_search_stocks_by_company_short_name(client, db_session):
    db_session.add(
        StockBasic(
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
    )
    db_session.commit()

    resp = client.get("/api/v1/stocks/search?q=環球晶")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["items"][0]["stock_code"] == "6488"
    assert data["items"][0]["market"] == "TPEX"


def test_search_stocks_filter_by_market(client, db_session):
    db_session.add_all(
        [
            StockBasic(
                stock_code="1234",
                market="TWSE",
                company_name="測試公司 A",
                company_short_name="測試A",
                industry="24",
                par_value=Decimal("10.0000"),
                listing_date=date(2020, 1, 1),
                capital_amount=100,
                issued_common_shares=10,
                source_name="TEST",
                source_url="https://example.test/a",
            ),
            StockBasic(
                stock_code="1235",
                market="TPEX",
                company_name="測試公司 B",
                company_short_name="測試B",
                industry="24",
                par_value=Decimal("10.0000"),
                listing_date=date(2020, 1, 1),
                capital_amount=100,
                issued_common_shares=10,
                source_name="TEST",
                source_url="https://example.test/b",
            ),
        ]
    )
    db_session.commit()

    resp = client.get("/api/v1/stocks/search?q=測試&market=TPEX")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["items"][0]["market"] == "TPEX"


def test_search_stocks_limit_and_offset(client, db_session):
    db_session.add_all(
        [
            StockBasic(
                stock_code="1001",
                market="TWSE",
                company_name="甲公司",
                company_short_name="甲",
                industry="24",
                par_value=Decimal("10.0000"),
                listing_date=date(2020, 1, 1),
                capital_amount=100,
                issued_common_shares=10,
                source_name="TEST",
                source_url="https://example.test/1001",
            ),
            StockBasic(
                stock_code="1002",
                market="TWSE",
                company_name="乙公司",
                company_short_name="乙",
                industry="24",
                par_value=Decimal("10.0000"),
                listing_date=date(2020, 1, 1),
                capital_amount=100,
                issued_common_shares=10,
                source_name="TEST",
                source_url="https://example.test/1002",
            ),
            StockBasic(
                stock_code="1003",
                market="TWSE",
                company_name="丙公司",
                company_short_name="丙",
                industry="24",
                par_value=Decimal("10.0000"),
                listing_date=date(2020, 1, 1),
                capital_amount=100,
                issued_common_shares=10,
                source_name="TEST",
                source_url="https://example.test/1003",
            ),
        ]
    )
    db_session.commit()

    resp = client.get("/api/v1/stocks/search?q=10&limit=1&offset=1")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert len(data["items"]) == 1


def test_search_stocks_invalid_query_returns_422(client):
    resp = client.get("/api/v1/stocks/search?q=   ")
    assert resp.status_code == 422

    data = resp.json()
    assert data["detail"]["code"] == "INVALID_QUERY"


def test_search_stocks_invalid_market_returns_422(client):
    resp = client.get("/api/v1/stocks/search?q=2330&market=BAD")
    assert resp.status_code == 422

    data = resp.json()
    assert data["detail"]["code"] == "INVALID_MARKET"


def _seed_stock_search_data(db_session):
    rows = [
        StockBasic(
            stock_code="2330",
            market="TWSE",
            company_name="台灣積體電路製造股份有限公司",
            company_short_name="台積電",
            industry="24",
            par_value=Decimal("10.0000"),
            capital_amount=100,
            issued_common_shares=10,
            listing_date=date(1994, 9, 5),
            source_name="TEST",
            source_url="https://example.test/2330",
        ),
        StockBasic(
            stock_code="2317",
            market="TWSE",
            company_name="鴻海精密工業股份有限公司",
            company_short_name="鴻海",
            industry="24",
            par_value=Decimal("10.0000"),
            capital_amount=100,
            issued_common_shares=10,
            listing_date=date(1991, 6, 18),
            source_name="TEST",
            source_url="https://example.test/2317",
        ),
        StockBasic(
            stock_code="6488",
            market="TPEX",
            company_name="環球晶圓股份有限公司",
            company_short_name="環球晶",
            industry="24",
            par_value=Decimal("10.0000"),
            capital_amount=100,
            issued_common_shares=10,
            listing_date=date(2015, 9, 25),
            source_name="TEST",
            source_url="https://example.test/6488",
        ),
    ]
    db_session.add_all(rows)
    db_session.commit()


def test_search_stocks_by_code(client, db_session):
    _seed_stock_search_data(db_session)

    resp = client.get("/api/v1/stocks/search?q=2330")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["total_count"] == 1
    assert data["items"][0]["stock_code"] == "2330"


def test_search_stocks_by_name(client, db_session):
    _seed_stock_search_data(db_session)

    resp = client.get("/api/v1/stocks/search?q=台積")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["total_count"] == 1
    assert data["items"][0]["company_short_name"] == "台積電"


def test_search_stocks_by_market(client, db_session):
    _seed_stock_search_data(db_session)

    resp = client.get("/api/v1/stocks/search?q=環球晶&market=TPEX")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["total_count"] == 1
    assert data["items"][0]["market"] == "TPEX"


def test_search_stocks_limit_and_offset(client, db_session):
    _seed_stock_search_data(db_session)

    resp = client.get("/api/v1/stocks/search?q=2&limit=1&offset=1")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["total_count"] >= 2
    assert len(data["items"]) == 1
