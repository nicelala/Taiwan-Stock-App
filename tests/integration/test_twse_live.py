import os
import pytest

from app.crawlers.tpex_client import TPExClient


pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION") != "1",
    reason="set RUN_INTEGRATION=1 to run live integration tests",
)
def test_tpex_live_stock_basic():
    rows = TPExClient().fetch_stock_basic_all()
    assert isinstance(rows, list)
    assert len(rows) > 0
    assert any(str(r.get("公司代號", "")).strip() == "6488" for r in rows)


@pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION") != "1",
    reason="set RUN_INTEGRATION=1 to run live integration tests",
)
def test_tpex_live_dividend():
    rows = TPExClient().fetch_dividend_all()
    assert isinstance(rows, list)
    assert len(rows) > 0