from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.dividend_history import DividendHistory
from app.models.stock_basic import StockBasic


HEADERS = [
    "股票代號",
    "市場",
    "公司名稱",
    "公司簡稱",
    "產業代碼",
    "產業名稱",
    "股利年度(民國)",
    "股利年度(西元)",
    "期別",
    "現金股利",
    "股票股利",
    "總股利",
]


def _fmt_decimal(v: Decimal | None) -> str:
    try:
        if v is None:
            return ""
        return str(v)  # ✅ 不再強制轉 Decimal
    except:
        return ""


def _to_roc_year(ad_year: int) -> int:
    return ad_year - 1911


def _get_year_window(db: Session) -> tuple[int, int]:
    """
    Q1=B：最近三年
    以本機 dividend_history 中最大的 dividend_year 當 max_year
    匯出 [max_year-2, max_year]
    """
    max_year = db.query(DividendHistory.dividend_year).order_by(DividendHistory.dividend_year.desc()).limit(1).scalar()
    if max_year is None:
        # 沒資料就回一個不會匯出任何資料的範圍
        return (0, 0)
    return (max_year - 2, max_year)


def export_market(db: Session, market: str, out_path: Path, year_from: int, year_to: int) -> int:
    """
    匯出指定 market + 年度範圍 的股利資料為 TSV。
    由於 DividendHistory 沒有公司名稱/簡稱欄位，因此 join StockBasic 取得。[1](https://usiglobaltw-my.sharepoint.com/personal/jason_wang_usiglobal_com/Documents/Microsoft%20Copilot%20Chat%20%E6%AA%94%E6%A1%88/dividend_history.py)[2](https://usiglobaltw-my.sharepoint.com/personal/jason_wang_usiglobal_com/Documents/Microsoft%20Copilot%20Chat%20%E6%AA%94%E6%A1%88/dividend_repository.py)
    """
    q = (
        db.query(DividendHistory, StockBasic)
        .join(StockBasic, DividendHistory.stock_id == StockBasic.id)
        .filter(DividendHistory.market == market)
        .filter(DividendHistory.dividend_year >= year_from)
        .filter(DividendHistory.dividend_year <= year_to)
        .order_by(DividendHistory.dividend_year.desc(), StockBasic.stock_code.asc(), DividendHistory.id.desc())
    )

    rows = q.all()

    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(HEADERS)


        for row in rows:

            if not row:
                continue

            if not isinstance(row, tuple) or len(row) < 2:
                continue

            dh, sb = row

            if dh is None or sb is None:
                continue

            if dh.dividend_year is None:
                continue
            ad_year = dh.dividend_year
            roc_year = _to_roc_year(ad_year)

            # 產業代碼/產業名稱：你的 StockBasic 欄位不一定有 industry_code
            # 這裡保守處理：產業代碼留空，產業名稱用 sb.industry（若有）[2](https://usiglobaltw-my.sharepoint.com/personal/jason_wang_usiglobal_com/Documents/Microsoft%20Copilot%20Chat%20%E6%AA%94%E6%A1%88/dividend_repository.py)
            industry_code = ""
            industry_name = getattr(sb, "industry", "") or ""

            w.writerow(
                [
                    dh.stock_code or "",
                    dh.market or "",
                    getattr(sb, "company_name", "") or "",
                    getattr(sb, "company_short_name", "") or "",
                    industry_code,
                    industry_name,
                    str(roc_year),
                    str(ad_year),
                    dh.period_label or "",
                    _fmt_decimal(dh.cash_dividend_per_share),
                    _fmt_decimal(dh.stock_dividend_per_share),
                    _fmt_decimal(dh.total_dividend_per_share),
                ]
            )

    return len(rows)


def main():
    project_root = Path(__file__).resolve().parents[1]
    out_twse = project_root / "dividends_TWSE_import.tsv"
    out_tpex = project_root / "dividends_TPEX_import.tsv"

    db = SessionLocal()
    try:
        year_from, year_to = _get_year_window(db)
        if year_from == 0:
            print("[WARN] no dividend_history data found in local DB; nothing exported.")
            return

        n1 = export_market(db, "TWSE", out_twse, year_from, year_to)
        print(f"[OK] export TWSE dividends rows={n1} -> {out_twse.name} (year {year_from}~{year_to})")

        n2 = export_market(db, "TPEX", out_tpex, year_from, year_to)
        print(f"[OK] export TPEX dividends rows={n2} -> {out_tpex.name} (year {year_from}~{year_to})")

    finally:
        db.close()


if __name__ == "__main__":
    main()