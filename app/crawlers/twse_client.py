from __future__ import annotations

import csv
import io
import logging
from typing import Any

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class TWSEClient:
    STOCK_BASIC_ENDPOINT = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
    STOCK_BASIC_CSV_ENDPOINT = "https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv"

    def fetch_stock_basic_all(self) -> list[dict[str, Any]]:
        return self._get_csv_dict_rows(self.STOCK_BASIC_CSV_ENDPOINT)

    def _request_get(self, url: str) -> requests.Response:
        headers = {
            "User-Agent": settings.user_agent,
            "Accept": "text/csv,application/csv;q=0.9,*/*;q=0.8",
        }
        timeout = getattr(settings, "request_timeout", 20)
        return requests.get(url, headers=headers, timeout=timeout)

    def _get_csv_dict_rows(self, url: str) -> list[dict[str, Any]]:
        resp = self._request_get(url)

        status = resp.status_code
        content_type = (resp.headers.get("content-type") or "").lower()

        if status != 200:
            preview = (resp.text or "")[:200]
            logger.error(
                "TWSE CSV fetch failed: url=%s status=%s content_type=%s preview=%r",
                url, status, content_type, preview
            )
            raise ValueError(f"TWSE_CSV_FETCH_FAILED status={status}")

        raw_bytes = resp.content or b""
        if not raw_bytes:
            logger.error(
                "TWSE CSV fetch returned empty body: url=%s status=%s content_type=%s",
                url, status, content_type
            )
            raise ValueError("TWSE_CSV_EMPTY_BODY")

        text = raw_bytes.decode("utf-8-sig", errors="replace")
        text_stripped = text.strip()

        # ✅ 新增：如果回來是 HTML（常見是安全阻擋頁），直接丟錯
        if "text/html" in content_type or text_stripped.lower().startswith("<html"):
            preview = text_stripped[:200].replace("\n", "\\n").replace("\r", "\\r")
            logger.error(
                "TWSE CSV endpoint returned HTML (blocked?): url=%s status=%s content_type=%s preview=%s",
                url, status, content_type, preview
            )
            raise ValueError("TWSE_CSV_BLOCKED_HTML")

        if not text_stripped:
            logger.error(
                "TWSE CSV fetch returned blank text: url=%s status=%s content_type=%s",
                url, status, content_type
            )
            raise ValueError("TWSE_CSV_BLANK_TEXT")

        # parse
        f = io.StringIO(text_stripped)
        reader = csv.DictReader(f)

        # ✅ 新增：檢查 header 是否包含你 normalize 會用到的「公司代號」
        headers = [h.strip() for h in (reader.fieldnames or []) if h]
        if "公司代號" not in headers:
            preview = text_stripped.splitlines()[0][:200]
            logger.error(
                "TWSE CSV header missing 公司代號: url=%s headers=%r first_line=%r",
                url, headers, preview
            )
            raise ValueError("TWSE_CSV_BAD_HEADER")

        rows: list[dict[str, Any]] = []
        for row in reader:
            if not row:
                continue
            cleaned = {k.strip(): v for k, v in row.items() if k is not None}
            rows.append(cleaned)

        if not rows:
            preview = text_stripped[:200].replace("\n", "\\n").replace("\r", "\\r")
            logger.warning(
                "TWSE CSV parsed 0 rows: url=%s content_type=%s preview=%s",
                url, content_type, preview
            )

        else:
            # 只印一次，方便你確認 keys 正確
            logger.info("TWSE CSV first row keys=%r", list(rows[0].keys())[:20])

        return rows