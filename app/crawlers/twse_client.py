from __future__ import annotations

import csv
import io
import logging
from typing import Any

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class TWSEClient:
    """
    TWSE data client.

    由於在雲端環境（例如 Render）呼叫 TWSE OpenAPI JSON 端點可能回傳非 JSON 的阻擋頁，
    這裡將「上市公司基本資料」改為使用 CSV 來源，以提高穩定性。

    CSV 來源（上市公司基本資料）：
    https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv
    """

    # 原 JSON 端點（保留常數方便對照/未來回切）
    STOCK_BASIC_ENDPOINT = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"

    # 改用 CSV 端點（上市公司基本資料）
    STOCK_BASIC_CSV_ENDPOINT = "https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv"

    def fetch_stock_basic_all(self) -> list[dict[str, Any]]:
        """
        取得上市公司基本資料（TWSE）。

        回傳格式：list[dict]，dict 的 key 為 CSV header（中文欄名），例如：
        - 公司代號
        - 公司名稱
        - 公司簡稱
        - 產業別
        - 普通股每股面額
        - 上市日期
        - 實收資本額
        - 已發行普通股數或TDR原股發行股數
        """
        return self._get_csv_dict_rows(self.STOCK_BASIC_CSV_ENDPOINT)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _request_get(self, url: str) -> requests.Response:
        headers = {
            "User-Agent": settings.user_agent,
            "Accept": "text/csv,application/csv;q=0.9,*/*;q=0.8",
        }
        timeout = getattr(settings, "request_timeout", 20)
        resp = requests.get(url, headers=headers, timeout=timeout)
        return resp

    def _get_csv_dict_rows(self, url: str) -> list[dict[str, Any]]:
        resp = self._request_get(url)

        status = resp.status_code
        content_type = (resp.headers.get("content-type") or "").lower()

        if status != 200:
            preview = (resp.text or "")[:200]
            logger.error(
                "TWSE CSV fetch failed: url=%s status=%s content_type=%s preview=%r",
                url,
                status,
                content_type,
                preview,
            )
            raise ValueError(f"TWSE_CSV_FETCH_FAILED status={status}")

        # 常見情況：CSV 可能帶 BOM，使用 utf-8-sig 可自動去除 BOM
        raw_bytes = resp.content or b""
        if not raw_bytes:
            logger.error(
                "TWSE CSV fetch returned empty body: url=%s status=%s content_type=%s",
                url,
                status,
                content_type,
            )
            raise ValueError("TWSE_CSV_EMPTY_BODY")

        try:
            text = raw_bytes.decode("utf-8-sig", errors="replace")
        except Exception as exc:
            logger.exception("TWSE CSV decode failed: url=%s err=%s", url, exc)
            raise ValueError("TWSE_CSV_DECODE_FAILED") from exc

        text_stripped = text.strip()
        if not text_stripped:
            logger.error(
                "TWSE CSV fetch returned blank text: url=%s status=%s content_type=%s",
                url,
                status,
                content_type,
            )
            raise ValueError("TWSE_CSV_BLANK_TEXT")

        # 用 DictReader 直接回傳 dict（key=中文欄名），方便沿用既有 normalize
        try:
            f = io.StringIO(text_stripped)
            reader = csv.DictReader(f)
            rows: list[dict[str, Any]] = []
            for row in reader:
                # csv.DictReader 可能回 None key（格式異常），避免污染
                if not row:
                    continue
                cleaned = {k: v for k, v in row.items() if k is not None}
                rows.append(cleaned)

        except Exception as exc:
            preview = text_stripped[:200]
            logger.exception(
                "TWSE CSV parse failed: url=%s status=%s content_type=%s preview=%r err=%s",
                url,
                status,
                content_type,
                preview,
                exc,
            )
            raise ValueError("TWSE_CSV_PARSE_FAILED") from exc

        if not rows:
            # 不直接 raise，讓上層看 count=0，並在 log 留線索
            preview = text_stripped[:200]
            logger.warning(
                "TWSE CSV parsed 0 rows: url=%s status=%s content_type=%s preview=%r",
                url,
                status,
                content_type,
                preview,
            )

        return rows