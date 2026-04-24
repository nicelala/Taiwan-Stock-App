from __future__ import annotations

import re
from datetime import date, datetime, UTC
from decimal import Decimal
from typing import Any


def parse_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None

    text = str(value).strip()
    if text in ("", "-", "--", "N/A", "None", "nan"):
        return None

    match = re.search(r"-?\d+(?:,\d{3})*(?:\.\d+)?", text)
    if not match:
        return None

    num = match.group(0).replace(",", "")
    try:
        return Decimal(num)
    except Exception:
        return None


def parse_date(value: Any) -> date | None:
    if value is None:
        return None

    text = str(value).strip()
    if text in ("", "-", "--", "N/A", "None"):
        return None

    if "/" in text:
        parts = text.split("/")
        if len(parts) == 3:
            y, m, d = parts
            y = int(y)
            m = int(m)
            d = int(d)
            if y < 1911:
                y += 1911
            return date(y, m, d)

    if text.isdigit():
        if len(text) == 8:
            return date(int(text[0:4]), int(text[4:6]), int(text[6:8]))
        elif len(text) == 7:
            y = int(text[0:3]) + 1911
            return date(y, int(text[3:5]), int(text[5:7]))

    return None


def split_code_and_name(raw_code_name: Any) -> tuple[str | None, str | None]:
    if raw_code_name is None:
        return None, None

    text = str(raw_code_name).strip()
    if not text:
        return None, None

    match = re.match(r"^(\d{4,6})\s*(.*)$", text)
    if match:
        code = match.group(1)
        name = match.group(2).strip() or None
        return code, name

    return None, text


def get_first(raw: dict, *keys: str):
    for key in keys:
        if key in raw:
            value = raw.get(key)
            if value not in (None, "", "-", "--"):
                return value
    return None


def fix_mojibake(value: Any) -> str | None:
    """
    修復常見 UTF-8 被當 latin1/cp1252 解碼造成的亂碼。
    例如：
    台積電 -> å°ç©é»
    """
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    # 若看起來已經是正常中文，就直接回傳
    if any("\u4e00" <= ch <= "\u9fff" for ch in text):
        return text

    # 嘗試把 mojibake 修回 UTF-8
    try:
        repaired = text.encode("latin1").decode("utf-8")
        return repaired
    except Exception:
        pass

    try:
        repaired = text.encode("cp1252").decode("utf-8")
        return repaired
    except Exception:
        pass

    return text


def now_utc() -> datetime:
    """
    以新的寫法取得 UTC 時間，並維持 naive UTC datetime，
    以避免影響目前 SQLAlchemy / API 既有輸出格式。
    """
    return datetime.now(UTC).replace(tzinfo=None)