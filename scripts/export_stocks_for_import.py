import csv
from datetime import date

from app.db.session import SessionLocal
from app.models.stock_basic import StockBasic  # 若你的 model 名稱不同，改成正確的
# 上面這行如果找不到，告訴我你 stock model 檔名/類別名，我改成正確 import

HEADERS = ["公司代號", "公司名稱", "公司簡稱", "產業別", "上市日期"]

def to_yyyy_mm_dd(d):
    if d is None:
        return ""
    if isinstance(d, (date, )):
        return d.strftime("%Y/%m/%d")
    return str(d)

def export_market(market: str, out_path: str):
    db = SessionLocal()
    try:
        rows = (
            db.query(StockBasic)
            .filter(StockBasic.market == market)
            .order_by(StockBasic.stock_code.asc())
            .all()
        )

        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(HEADERS)
            for r in rows:
                w.writerow([
                    r.stock_code or "",
                    r.company_name or "",
                    r.company_short_name or "",
                    r.industry or "",
                    to_yyyy_mm_dd(r.listing_date),
                ])

        print(f"[OK] export {market} rows={len(rows)} -> {out_path}")
    finally:
        db.close()

if __name__ == "__main__":
    export_market("TWSE", "stocks_TWSE_import.csv")
    export_market("TPEX", "stocks_TPEX_import.csv")