from __future__ import annotations

import json
import requests

from app.core.config import settings
import logging


logger = logging.getLogger(__name__)
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

        content_type = resp.headers.get("content-type", "")
        if not raw_text.strip():
            logger.error(
                "TWSE _get_json got empty body: url=%s status=%s content_type=%s content_len=%s",
                url,
                resp.status_code,
                content_type,
                len(resp.content),
            )
            raise ValueError(f"TWSE endpoint returned empty body: {url} status={resp.status_code} content_type={content_type}")
        
        if "json" not in content_type.lower():
            preview = raw_text[:200].replace("\n", "\\n").replace("\r", "\\r")
            logger.error(
                "TWSE _get_json got non-json response: url=%s status=%s content_type=%s preview=%s",
                url,
                resp.status_code,
                content_type,
                preview,
            )
            raise ValueError(f"TWSE endpoint returned non-json content: {url} status={resp.status_code} content_type={content_type}")
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            preview = raw_text[:200].replace("\n", "\\n").replace("\r", "\\r")
            logger.error(
                "TWSE _get_json JSON decode failed: url=%s status=%s content_type=%s preview=%s",
                url,
                resp.status_code,
                content_type,
                preview,
            )
            raise

    def fetch_stock_basic_all(self) -> list:
        return self._get_json(self.STOCK_BASIC_ENDPOINT)

    def fetch_dividend_all(self) -> list:
        return self._get_json(self.DIVIDEND_ENDPOINT)