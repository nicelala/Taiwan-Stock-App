from decimal import Decimal
from datetime import date

from app.repositories.stock_repository import StockRepository
from app.repositories.dividend_repository import DividendRepository
from app.models.stock_basic import StockBasic
from app.models.dividend_history import DividendHistory


def test_stock_repository_upsert_insert_and_update(db_session):
    repo = StockRepository(db_session)

    payload_insert = {
        "stock_code": "2330",
        "market": "TWSE",
        "company_name": "台灣積體電路製造股份有限公司",
        "company_short_name": "台積電",
        "industry": "24",
        "par_value": Decimal("10.0000"),
        "listing_date": date(1994, 9, 5),
        "capital_amount": 100,
        "issued_common_shares": 10,
        "source_name": "TEST",
        "source_url": "https://example.test",
    }

    obj = repo.upsert_one(payload_insert)
    db_session.commit()

    assert obj.id is not None

    payload_update = dict(payload_insert)
    payload_update["company_short_name"] = "TSMC"

    obj2 = repo.upsert_one(payload_update)
    db_session.commit()

    row = db_session.query(StockBasic).filter_by(stock_code="2330", market="TWSE").first()
    assert row is not None
    assert row.company_short_name == "TSMC"


def test_stock_repository_allows_same_code_in_different_markets(db_session):
    repo = StockRepository(db_session)

    repo.upsert_one(
        {
            "stock_code": "9999",
            "market": "TWSE",
            "company_name": "測試上市公司",
            "company_short_name": "上市測試",
            "industry": "24",
            "par_value": Decimal("10.0000"),
            "listing_date": date(2020, 1, 1),
            "capital_amount": 100,
            "issued_common_shares": 10,
            "source_name": "TEST",
            "source_url": "https://example.test/twse",
        }
    )

    repo.upsert_one(
        {
            "stock_code": "9999",
            "market": "TPEX",
            "company_name": "測試上櫃公司",
            "company_short_name": "上櫃測試",
            "industry": "24",
            "par_value": Decimal("10.0000"),
            "listing_date": date(2020, 1, 1),
            "capital_amount": 100,
            "issued_common_shares": 10,
            "source_name": "TEST",
            "source_url": "https://example.test/tpex",
        }
    )

    db_session.commit()

    rows = db_session.query(StockBasic).filter_by(stock_code="9999").all()
    assert len(rows) == 2

    markets = sorted([r.market for r in rows])
    assert markets == ["TPEX", "TWSE"]


def test_dividend_repository_upsert_insert_and_update(db_session):
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
        source_url="https://example.test",
    )
    db_session.add(stock)
    db_session.commit()
    db_session.refresh(stock)

    repo = DividendRepository(db_session)

    payload_insert = {
        "stock_id": stock.id,
        "stock_code": "2330",
        "market": "TWSE",
        "dividend_year": 114,
        "belongs_to_year_or_period": "114",
        "period_label": "1",
        "resolution_status": "董事會決議",
        "board_approved_date": date(2026, 2, 10),
        "shareholder_meeting_date": None,
        "cash_dividend_per_share": Decimal("6.0000"),
        "stock_dividend_per_share": Decimal("0.0000"),
        "total_dividend_per_share": Decimal("6.0000"),
        "stock_dividend_rate_pct": None,
        "par_value": None,
        "source_name": "TEST",
        "source_url": "https://example.test/dividend",
        "biz_key": "2330|TWSE|114|1|2026-02-10|董事會決議",
    }

    obj = repo.upsert_one(payload_insert)
    db_session.commit()
    assert obj.id is not None

    payload_update = dict(payload_insert)
    payload_update["cash_dividend_per_share"] = Decimal("6.5000")
    payload_update["total_dividend_per_share"] = Decimal("6.5000")

    obj2 = repo.upsert_one(payload_update)
    db_session.commit()

    row = db_session.query(DividendHistory).filter_by(
        biz_key="2330|TWSE|114|1|2026-02-10|董事會決議"
    ).first()

    assert row is not None
    assert row.cash_dividend_per_share == Decimal("6.5000")


def test_dividend_repository_list_by_stock_code_supports_tpex(db_session):
    stock = StockBasic(
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
        source_url="https://example.test",
    )
    db_session.add(stock)
    db_session.commit()
    db_session.refresh(stock)

    db_session.add(
        DividendHistory(
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
    )
    db_session.commit()

    repo = DividendRepository(db_session)
    rows = repo.list_by_stock_code("6488", "TPEX")

    assert len(rows) == 1
    assert rows[0].market == "TPEX"
    assert rows[0].stock_code == "6488"