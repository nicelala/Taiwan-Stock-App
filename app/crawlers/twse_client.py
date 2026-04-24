from __future__ import annotations

import json
import requests

from app.core.config import settings


class TWSEClient:
    BASE_URL = "https://openapi.twse.com.tw/v1"

    STOCK_BASIC_ENDPOINT = "/opendata/t187ap03_L"
    DIVIDEND_ENDPOINT = "/opendata/t187ap45_L"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": settings.user_agent,
            "Accept": "application/json",
        })
        self.timeout = settings.request_timeout

    def _get_json(self, endpoint: str) -> list:
        url = f"{self.BASE_URL}{endpoint}"
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()

        # 明確以 utf-8-sig 解碼，避免 requests 自行猜錯
        raw_text = resp.content.decode("utf-8-sig", errors="strict")
        return json.loads(raw_text)

    def fetch_stock_basic_all(self) -> list:
        return self._get_json(self.STOCK_BASIC_ENDPOINT)

    def fetch_dividend_all(self) -> list:
        return self._get_json(self.DIVIDEND_ENDPOINT)