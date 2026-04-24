from __future__ import annotations

import csv
import io
import requests

from app.core.config import settings


class TPExClient:
    """
    TPEx 上櫃資料 crawler
    目前第 2-1 批只會用到股票基本資料
    """

    # 上櫃公司基本資料（官方開放資料 CSV）
    STOCK_BASIC_URL = "https://mopsfin.twse.com.tw/opendata/t187ap03_O.csv"

    # 先保留給第 2-2 批（Dividend）用
    DIVIDEND_URL = "https://mopsfin.twse.com.tw/opendata/t187ap45_O.csv"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": settings.user_agent,
                "Accept": "*/*",
            }
        )
        self.timeout = settings.request_timeout

    def fetch_stock_basic_all(self) -> list[dict]:
        text = self._get_text(self.STOCK_BASIC_URL)
        return self._parse_csv(text)

    def fetch_dividend_all(self) -> list[dict]:
        text = self._get_text(self.DIVIDEND_URL)
        return self._parse_csv(text)

    def _get_text(self, url: str) -> str:
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.content.decode("utf-8-sig", errors="replace")

    def _parse_csv(self, text: str) -> list[dict]:
        reader = csv.DictReader(io.StringIO(text))
        return [row for row in reader]