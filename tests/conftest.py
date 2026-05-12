import os
import gc
import time
from pathlib import Path
from decimal import Decimal
from datetime import date

import pytest

# 先在 import app 之前指定測試 DB
TEST_DB_FILE = Path("test_tw_dividend.db").resolve()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_FILE.as_posix()}"

from fastapi.testclient import TestClient
from sqlalchemy.orm import close_all_sessions

from app.main import app
from app.api.deps import get_db
from app.db.init_db import init_db
from app.db.session import SessionLocal, engine
from app.models.stock_basic import StockBasic
from app.models.dividend_history import DividendHistory
from app.models.refresh_job_log import RefreshJobLog


def _safe_remove_db_file(path: Path, retries: int = 5, delay: float = 0.2) -> None:
    """
    Windows 下 SQLite 檔案常因連線尚未完全釋放而刪除失敗。
    這裡做簡單 retry。
    """
    for attempt in range(retries):
        try:
            if path.exists():
                path.unlink()
            return
        except PermissionError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)


@pytest.fixture(scope="session", autouse=True)
def prepare_test_db():
    """
    建立測試用 DB 檔。
    測試結束後自動刪除。
    """
    if TEST_DB_FILE.exists():
        _safe_remove_db_file(TEST_DB_FILE)

    init_db()

    yield

    # 關閉所有 ORM sessions
    close_all_sessions()

    # 釋放 SQLAlchemy engine 持有的 SQLite file handle
    engine.dispose()

    # 讓 Python 盡快回收可能殘留的物件引用
    gc.collect()

    _safe_remove_db_file(TEST_DB_FILE)


@pytest.fixture(autouse=True)
def clean_tables():
    """
    每個測試前清空資料，避免互相污染。
    """
    db = SessionLocal()
    try:
        db.query(RefreshJobLog).delete()
        db.query(DividendHistory).delete()
        db.query(StockBasic).delete()
        db.commit()
        yield
    finally:
        db.close()


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def seed_stock_basic(db_session):
    stock = StockBasic(
        stock_code="2330",
        market="TWSE",
        company_name="台灣積體電路製造股份有限公司",
        company_short_name="台積電",
        industry="24",
        par_value=Decimal("10.0000"),
        listing_date=date(1994, 9, 5),
        capital_amount=259325245210,
        issued_common_shares=25932524521,
        source_name="TEST",
        source_url="https://example.test/stock",
    )
    db_session.add(stock)
    db_session.commit()
    db_session.refresh(stock)
    return stock


@pytest.fixture
def seed_dividends(db_session, seed_stock_basic):
    items = [
        DividendHistory(
            stock_id=seed_stock_basic.id,
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
            source_url="https://example.test/dividend",
            biz_key="2330|TWSE|114|1|2026-02-10|董事會決議",
        ),
        DividendHistory(
            stock_id=seed_stock_basic.id,
            stock_code="2330",
            market="TWSE",
            dividend_year=113,
            belongs_to_year_or_period="113",
            period_label="1",
            resolution_status="董事會決議",
            board_approved_date=date(2025, 2, 15),
            shareholder_meeting_date=None,
            cash_dividend_per_share=Decimal("5.5000"),
            stock_dividend_per_share=Decimal("0.0000"),
            total_dividend_per_share=Decimal("5.5000"),
            stock_dividend_rate_pct=None,
            par_value=None,
            source_name="TEST",
            source_url="https://example.test/dividend",
            biz_key="2330|TWSE|113|1|2025-02-15|董事會決議",
        ),
    ]

    db_session.add_all(items)
    db_session.commit()
    return items