from datetime import datetime


def parse_float(value) -> float | None:
    if value in (None, "", "-", "NA", "N/A"):
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return None


def normalize_dividend_row(raw: dict, market: str) -> dict:
    """
    將不同來源欄位映射到統一格式
    注意：正式欄位名稱需依實際來源再調整
    """
    stock_code = raw.get("公司代號") or raw.get("公司代號名稱", "")[:4]
    dividend_year = raw.get("股利年度")

    cash_dividend = (
        parse_float(raw.get("股東配發內容-盈餘分配之現金股利 (元/股)")) or 0.0
    ) + (
        parse_float(raw.get("股東配發內容-法定盈餘公積、資本公積發放之現金 (元/股)")) or 0.0
    )

    stock_dividend = (
        parse_float(raw.get("股東配發內容-盈餘轉增資配股 (元/股)")) or 0.0
    ) + (
        parse_float(raw.get("股東配發內容-法定盈餘公積、資本公積轉增資配股 (元/股)")) or 0.0
    )

    board_date = raw.get("董事會決議（擬議）股利分派日") or raw.get("董事會決議通過股利分派日")
    period_label = raw.get("期別")

    biz_key = f"{stock_code}|{market}|{dividend_year}|{period_label}|{board_date}"

    return {
        "stock_code": stock_code,
        "market": market,
        "dividend_year": int(dividend_year) if dividend_year else None,
        "belongs_to_year_or_period": raw.get("股利所屬年 (季)度") or raw.get("股利所屬年度"),
        "period_label": period_label,
        "resolution_status": raw.get("決議（擬議）進度"),
        "cash_dividend_per_share": cash_dividend,
        "stock_dividend_per_share": stock_dividend,
        "total_dividend_per_share": cash_dividend + stock_dividend,
        "biz_key": biz_key,
        "source_name": "OFFICIAL_DIVIDEND",
        "source_updated_at": datetime.utcnow(),
    }