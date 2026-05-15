from __future__ import annotations

from decimal import Decimal
from app.core.utils import get_industry_name
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.schemas.stock import StockBasicResponse
from app.schemas.stock_search import StockSearchListResponse
from app.schemas.dividend import DividendListResponse
from app.schemas.dividend_search import DividendSearchListResponse
from app.schemas.refresh_job_log import RefreshJobLogListResponse
from app.schemas.scheduler import (
    SchedulerStatusResponse,
    SchedulerJobsListResponse,
    SchedulerControlResponse,
    SchedulerRunNowResponse,
)
from app.services.stock_service import StockService
from app.services.stock_search_service import StockSearchService
from app.services.dividend_service import DividendService
from app.services.dividend_search_service import DividendSearchService
from app.services.refresh_job_log_service import RefreshJobLogService
from app.services.scheduler_service import SchedulerService

import csv
import io
from datetime import datetime, timezone

from app.repositories.dividend_repository import DividendRepository
from fastapi.responses import StreamingResponse
from openpyxl import Workbook


from fastapi import File, Header, UploadFile
from app.repositories.stock_repository import StockRepository
from app.core.utils import parse_date, fix_mojibake


router = APIRouter(prefix="/api/v1")

REFRESH_LOGS_EXPORT_CSV_MAX = 200_000

REFRESH_LOGS_EXPORT_FIELDS = [
    "id",
    "job_name",
    "market",
    "status",
    "started_at",
    "finished_at",
    "duration_ms",
    "inserted_or_updated_count",
    "skipped_count",
    "error_message",
    "trigger_source",
]

DIVIDENDS_EXPORT_CSV_MAX = 200_000
DIVIDENDS_EXPORT_XLSX_MAX = 20_000

# 欄位順序：沿用 API 原順序（DividendSearchService._to_response_items 的 dict 插入順序）
DIVIDENDS_EXPORT_FIELDS = [
    "stock_code",
    "market",
    "company_name",
    "company_short_name",
    "industry",
    "industry_name",
    "dividend_year",
    "dividend_year_ad",
    "period_label",
    "cash_dividend_per_share",
    "stock_dividend_per_share",
    "total_dividend_per_share",
]

# 中文 header（順序需與 DIVIDENDS_EXPORT_FIELDS 完全一致）
DIVIDENDS_EXPORT_HEADERS_ZH = [
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

def _iter_csv_with_bom(rows: list[dict], fields: list[str], headers: list[str]):
    """
    以 StreamingResponse 輸出 CSV（UTF-8 with BOM），header 使用 API keys。
    欄位順序固定依 fields。
    """
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    # header（第一段包含 BOM）
    writer.writerow(headers)
    header_text = output.getvalue()
    output.seek(0)
    output.truncate(0)
    yield "\ufeff" + header_text

    # data rows
    for r in rows:
        writer.writerow([r.get(f, "") if r.get(f, "") is not None else "" for f in fields])
        chunk = output.getvalue()
        output.seek(0)
        output.truncate(0)
        yield chunk

def _build_xlsx_bytes(rows: list[dict], fields: list[str], headers: list[str]) -> bytes:
    """
    產生 XLSX bytes（純資料、header 中文），欄位值依 fields 順序取出。
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "dividends"

    # header（中文）
    ws.append(headers)

    # data rows
    for r in rows:
        ws.append([r.get(f, "") if r.get(f, "") is not None else "" for f in fields])

    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)
    return bio.getvalue()

@router.get("/dividends/export")
def export_dividends(
    format: str = Query(default="csv", description="csv or xlsx"),
    market: str | None = Query(default=None, description="TWSE or TPEX"),
    year: int | None = Query(default=None),
    cash_min: Decimal | None = Query(default=None),
    stock_min: Decimal | None = Query(default=None),
    total_min: Decimal | None = Query(default=None),
    sort_by: str = Query(default="total", description="cash, stock, total, year, code"),
    sort_dir: str = Query(default="desc", description="asc or desc"),
    db: Session = Depends(get_db),
):
    # 目前先實作 csv；xlsx 下一階段再補
    fmt = (format or "").strip().lower()
    if fmt not in {"csv", "xlsx"}:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_EXPORT_FORMAT",
                "message": "format must be csv or xlsx",
            },
        )

    # 參數驗證（與 /dividends/search 保持一致）
    if market is not None and market.strip().upper() not in {"TWSE", "TPEX"}:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_MARKET",
                "message": "market must be TWSE or TPEX",
            },
        )

    if sort_by.strip().lower() not in {"cash", "stock", "total", "year", "code"}:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_SORT_BY",
                "message": "sort_by must be one of: cash, stock, total, year, code",
            },
        )

    if sort_dir.strip().lower() not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_SORT_DIR",
                "message": "sort_dir must be asc or desc",
            },
        )

    # 忽略 page/page_size：直接抓全量（但受上限保護）
    service = DividendSearchService(db)
    repo = DividendRepository(db)

    # 第一次查：只為了拿 total_count（repo.search 會 count）
    _rows_1, total_count = repo.search(
        market=market.strip().upper() if market is not None else None,
        year=year,
        cash_min=cash_min,
        stock_min=stock_min,
        total_min=total_min,
        sort_by=sort_by.strip().lower(),
        sort_dir=sort_dir.strip().lower(),
        limit=1,
        offset=0,
    )

    max_limit = DIVIDENDS_EXPORT_CSV_MAX if fmt == "csv" else DIVIDENDS_EXPORT_XLSX_MAX

    if total_count > max_limit:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "EXPORT_TOO_LARGE",
                "message": f"export rows ({total_count}) exceeds limit ({max_limit})",
            },
        )

    # 第二次查：真正拿資料（最多 total_count 筆）
    if total_count == 0:
        items: list[dict] = []
    else:
        rows, _ = repo.search(
            market=market.strip().upper() if market is not None else None,
            year=year,
            cash_min=cash_min,
            stock_min=stock_min,
            total_min=total_min,
            sort_by=sort_by.strip().lower(),
            sort_dir=sort_dir.strip().lower(),
            limit=total_count,
            offset=0,
        )
        # 沿用 API 原順序輸出 dict
        items = service._to_response_items(rows)  # noqa: SLF001

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
    filename = f"dividends_export_{ts}.csv"

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")

    if fmt == "csv":
        filename = f"dividends_export_{ts}.csv"
        return StreamingResponse(
            _iter_csv_with_bom(items, DIVIDENDS_EXPORT_FIELDS, DIVIDENDS_EXPORT_HEADERS_ZH),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    # fmt == "xlsx"
    filename = f"dividends_export_{ts}.xlsx"
    xlsx_bytes = _build_xlsx_bytes(items, DIVIDENDS_EXPORT_FIELDS, DIVIDENDS_EXPORT_HEADERS_ZH)
    return StreamingResponse(
        io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/stocks/search", response_model=StockSearchListResponse)
def search_stocks(
    q: str = Query(..., min_length=1),
    market: str | None = Query(default=None, description="TWSE or TPEX"),
    limit: int = Query(default=20),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
):

    if not q.strip():
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_QUERY",
                "message": "q must not be blank",
            },
        )

    service = StockService(db)

    try:
        items, total_count = service.search(
            q=q,
            market=market,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_MARKET",
                    "message": "market must be TWSE or TPEX",
                },
            )
        raise

    return {
        "items": items,
        "count": len(items),
        "total_count": total_count,
    }


@router.get("/dividends/search", response_model=DividendSearchListResponse)
def search_dividends(
    market: str | None = Query(default=None, description="TWSE or TPEX"),
    year: int | None = Query(default=None),
    cash_min: Decimal | None = Query(default=None),
    stock_min: Decimal | None = Query(default=None),
    total_min: Decimal | None = Query(default=None),
    sort_by: str = Query(default="total", description="cash, stock, total, year, code"),
    sort_dir: str = Query(default="desc", description="asc or desc"),
    limit: int = Query(default=20),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
):
    service = DividendSearchService(db)

    try:
        items, total_count = service.search(
            market=market,
            year=year,
            cash_min=cash_min,
            stock_min=stock_min,
            total_min=total_min,
            sort_by=sort_by,
            sort_dir=sort_dir,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_MARKET",
                    "message": "market must be TWSE or TPEX",
                },
            )
        if str(exc) == "INVALID_SORT_BY":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_SORT_BY",
                    "message": "sort_by must be one of: cash, stock, total, year, code",
                },
            )
        if str(exc) == "INVALID_SORT_DIR":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_SORT_DIR",
                    "message": "sort_dir must be asc or desc",
                },
            )
        raise

    return {
        "items": items,
        "count": len(items),
        "total_count": total_count,
    }


@router.get("/stocks/{stock_code}", response_model=StockBasicResponse)
def get_stock_basic(
    stock_code: str,
    market: str | None = Query(default=None, description="TWSE or TPEX"),
    fetch_remote: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    service = StockService(db)

    try:
        stock = service.get_stock(stock_code, market)
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_MARKET",
                    "message": "market must be TWSE or TPEX",
                },
            )
        if str(exc) == "MULTIPLE_MARKET_MATCH":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "MULTIPLE_MARKET_MATCH",
                    "message": f"stock_code={stock_code} exists in multiple markets, please specify ?market=TWSE or ?market=TPEX",
                },
            )
        raise

    if stock is None and (fetch_remote or settings.auto_fetch_on_miss):
        try:
            stock = service.sync_one_if_missing(stock_code, market)
        except ValueError as exc:
            if str(exc) == "INVALID_MARKET":
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "INVALID_MARKET",
                        "message": "market must be TWSE or TPEX",
                    },
                )
            if str(exc) == "MULTIPLE_MARKET_MATCH":
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "MULTIPLE_MARKET_MATCH",
                        "message": f"stock_code={stock_code} exists in multiple markets, please specify ?market=TWSE or ?market=TPEX",
                    },
                )
            raise

    if stock is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "STOCK_NOT_FOUND",
                "message": f"stock_code={stock_code} not found in local DB",
            },
        )

    return {
    "stock_code": stock.stock_code,
    "market": stock.market,
    "company_name": stock.company_name,
    "company_short_name": stock.company_short_name,
    "industry": stock.industry,
    "industry_name": get_industry_name(stock.industry),
    "par_value": stock.par_value,
    "capital_amount": stock.capital_amount,
    "issued_common_shares": stock.issued_common_shares,
    "listing_date": stock.listing_date,
}


@router.get("/stocks/{stock_code}/dividends", response_model=DividendListResponse)
def get_stock_dividends(
    stock_code: str,
    market: str | None = Query(default=None, description="TWSE or TPEX"),
    year_from: int | None = Query(default=None),
    year_to: int | None = Query(default=None),
    fetch_remote: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    if year_from is not None and year_to is not None and year_from > year_to:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_YEAR_RANGE",
                "message": "year_from cannot be greater than year_to",
            },
        )

    stock_service = StockService(db)

    try:
        stock = stock_service.get_stock(stock_code, market)
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_MARKET",
                    "message": "market must be TWSE or TPEX",
                },
            )
        if str(exc) == "MULTIPLE_MARKET_MATCH":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "MULTIPLE_MARKET_MATCH",
                    "message": f"stock_code={stock_code} exists in multiple markets, please specify ?market=TWSE or ?market=TPEX",
                },
            )
        raise

    if stock is None and (fetch_remote or settings.auto_fetch_on_miss):
        try:
            stock = stock_service.sync_one_if_missing(stock_code, market)
        except ValueError as exc:
            if str(exc) == "INVALID_MARKET":
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "INVALID_MARKET",
                        "message": "market must be TWSE or TPEX",
                    },
                )
            if str(exc) == "MULTIPLE_MARKET_MATCH":
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "MULTIPLE_MARKET_MATCH",
                        "message": f"stock_code={stock_code} exists in multiple markets, please specify ?market=TWSE or ?market=TPEX",
                    },
                )
            raise

    if stock is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "STOCK_NOT_FOUND",
                "message": f"stock_code={stock_code} not found in local DB",
            },
        )

    dividend_service = DividendService(db)
    resolved_market = stock.market

    try:
        items = dividend_service.list_dividends(
            stock_code=stock_code,
            market=resolved_market,
            year_from=year_from,
            year_to=year_to,
        )
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_MARKET",
                    "message": "market must be TWSE or TPEX",
                },
            )
        raise

    if not items and (fetch_remote or settings.auto_fetch_on_miss):
        try:
            items = dividend_service.sync_one_if_missing(stock_code, resolved_market)
        except ValueError as exc:
            if str(exc) == "INVALID_MARKET":
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "INVALID_MARKET",
                        "message": "market must be TWSE or TPEX",
                    },
                )
            raise

        if year_from is not None or year_to is not None:
            items = dividend_service.list_dividends(
                stock_code=stock_code,
                market=resolved_market,
                year_from=year_from,
                year_to=year_to,
            )

    return {
        "stock_code": stock_code,
        "market": resolved_market,
        "items": items,
    }


@router.post("/admin/refresh/stocks")
def refresh_stock_basic(
    market: str = Query(default="TWSE", description="TWSE or TPEX"),
    db: Session = Depends(get_db),
):
    service = StockService(db)

    try:
        result = service.sync_from_source(market)
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_MARKET",
                    "message": "market must be TWSE or TPEX",
                },
            )
        raise

    return result

@router.post("/admin/import/stocks")
def import_stocks_csv(
    market: str = Query(..., description="TWSE or TPEX"),
    file: UploadFile = File(...),
    x_admin_token: str | None = Header(default=None, alias="X-ADMIN-TOKEN"),
    db: Session = Depends(get_db),
):
    # --- auth ---
    if settings.admin_token is None:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "ADMIN_TOKEN_NOT_SET",
                "message": "ADMIN_TOKEN is not configured on server",
            },
        )

    if x_admin_token != settings.admin_token:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "UNAUTHORIZED",
                "message": "invalid admin token",
            },
        )

    # --- validate market ---
    market_text = str(market or "").strip().upper()
    if market_text not in {"TWSE", "TPEX"}:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_MARKET",
                "message": "market must be TWSE or TPEX",
            },
        )

    # --- read file ---
    raw = file.file.read()
    if not raw:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "EMPTY_FILE",
                "message": "uploaded file is empty",
            },
        )

    # 支援 BOM 的 utf-8-sig；若不是 utf-8 也會用 replace 先保命
    text = raw.decode("utf-8-sig", errors="replace").strip()
    if not text:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "EMPTY_FILE_TEXT",
                "message": "uploaded file has no readable text",
            },
        )

    reader = csv.DictReader(io.StringIO(text))

    def pick(row: dict, *keys: str):
        for k in keys:
            if k in row and row[k] is not None and str(row[k]).strip() != "":
                return row[k]
        return None

    repo = StockRepository(db)

    inserted_or_updated = 0
    skipped = 0

    for row in reader:
        # 允許兩種 header：中文或 API keys
        stock_code = pick(row, "公司代號", "stock_code")
        company_name = pick(row, "公司名稱", "company_name")
        company_short_name = pick(row, "公司簡稱", "company_short_name")
        industry = pick(row, "產業別", "industry")
        listing_date_raw = pick(row, "上市日期", "上櫃日期", "listing_date")

        stock_code = str(stock_code or "").strip() or None
        if stock_code is None:
            skipped += 1
            continue

        company_name = fix_mojibake(company_name) or ""
        company_short_name = fix_mojibake(company_short_name)
        industry = str(industry or "").strip() or None
        listing_date = parse_date(listing_date_raw)

        payload = {
            "stock_code": stock_code,
            "market": market_text,
            "company_name": company_name,
            "company_short_name": company_short_name,
            "industry": industry,

            # Q2=B：最小欄位，其餘欄位維持 None
            "par_value": None,
            "capital_amount": None,
            "issued_common_shares": None,
            "listing_date": listing_date,

            # 來源欄位
            "source_name": f"IMPORT_{market_text}",
            "source_url": "local_import",
        }

        repo.upsert_one(payload)
        inserted_or_updated += 1

    db.commit()

    return {
        "status": "success",
        "market": market_text,
        "count": inserted_or_updated,
        "skipped": skipped,
    }

@router.post("/admin/refresh/dividends")
def refresh_dividends(
    market: str = Query(default="TWSE", description="TWSE or TPEX"),
    db: Session = Depends(get_db),
):
    stock_service = StockService(db)
    dividend_service = DividendService(db)

    try:
        stock_service.sync_from_source(market)
        result = dividend_service.sync_from_source(market)
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_MARKET",
                    "message": "market must be TWSE or TPEX",
                },
            )
        if str(exc) == "MULTIPLE_MARKET_MATCH":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "MULTIPLE_MARKET_MATCH",
                    "message": "multiple market match",
                },
            )
        raise

    return result


@router.get("/admin/refresh/logs", response_model=RefreshJobLogListResponse)
def list_refresh_logs(
    job_name: str | None = Query(default=None, description="refresh_stocks or refresh_dividends"),
    market: str | None = Query(default=None, description="TWSE or TPEX"),
    status: str | None = Query(default=None, description="running, success, or failed"),
    limit: int = Query(default=20),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
):
    service = RefreshJobLogService(db)

    try:
        items = service.list_logs(
            job_name=job_name,
            market=market,
            status=status,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_MARKET",
                    "message": "market must be TWSE or TPEX",
                },
            )
        if str(exc) == "INVALID_STATUS":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_STATUS",
                    "message": "status must be running, success, or failed",
                },
            )
        if str(exc) == "INVALID_JOB_NAME":
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "INVALID_JOB_NAME",
                    "message": "job_name must be refresh_stocks or refresh_dividends",
                },
            )
        raise

    return {
        "items": items,
        "count": len(items),
    }

@router.get("/admin/refresh/logs/export")
def export_refresh_logs(
    format: str = Query(default="csv", description="csv"),
    job_name: str | None = Query(default=None, description="refresh_stocks or refresh_dividends"),
    market: str | None = Query(default=None, description="TWSE or TPEX"),
    status: str | None = Query(default=None, description="running, success, or failed"),
    db: Session = Depends(get_db),
):
    fmt = (format or "").strip().lower()
    if fmt != "csv":
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_EXPORT_FORMAT",
                "message": "format must be csv",
            },
        )

    service = RefreshJobLogService(db)

    # 先用 service 本身的驗證機制檢查參數（沿用既有 INVALID_* 行為）
    try:
        _ = service.list_logs(
            job_name=job_name,
            market=market,
            status=status,
            limit=1,
            offset=0,
        )
    except ValueError as exc:
        if str(exc) == "INVALID_MARKET":
            raise HTTPException(
                status_code=422,
                detail={"code": "INVALID_MARKET", "message": "market must be TWSE or TPEX"},
            )
        if str(exc) == "INVALID_STATUS":
            raise HTTPException(
                status_code=422,
                detail={"code": "INVALID_STATUS", "message": "status must be running, success, or failed"},
            )
        if str(exc) == "INVALID_JOB_NAME":
            raise HTTPException(
                status_code=422,
                detail={"code": "INVALID_JOB_NAME", "message": "job_name must be refresh_stocks or refresh_dividends"},
            )
        raise

    # 匯出忽略分頁：用 paging 把全部資料抓出來
    all_items: list[dict] = []
    offset = 0
    page_limit = 100  # RefreshJobLogService._normalize_limit 最高 100

    while True:
        batch = service.list_logs(
            job_name=job_name,
            market=market,
            status=status,
            limit=page_limit,
            offset=offset,
        )

        if not batch:
            break

        # batch 可能是 pydantic model 或 dict；統一轉成 dict
        for item in batch:
            if hasattr(item, "model_dump"):
                all_items.append(item.model_dump())
            elif isinstance(item, dict):
                all_items.append(item)
            else:
                # fallback：用 __dict__，避免類型不符導致匯出失敗
                all_items.append(getattr(item, "__dict__", {}))

        if len(all_items) > REFRESH_LOGS_EXPORT_CSV_MAX:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "EXPORT_TOO_LARGE",
                    "message": f"export rows ({len(all_items)}) exceeds limit ({REFRESH_LOGS_EXPORT_CSV_MAX})",
                },
            )

        offset += len(batch)

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
    filename = f"refresh_logs_export_{ts}.csv"

    # header 使用 API keys（你選 A），所以 headers = fields
    return StreamingResponse(
        _iter_csv_with_bom(all_items, REFRESH_LOGS_EXPORT_FIELDS, REFRESH_LOGS_EXPORT_FIELDS),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename=\"{filename}\"'},
    )

@router.get("/admin/scheduler/status", response_model=SchedulerStatusResponse)
def get_scheduler_status(request: Request):
    scheduler = getattr(request.app.state, "scheduler", None)
    service = SchedulerService()
    return service.get_status(scheduler)


@router.get("/admin/scheduler/jobs", response_model=SchedulerJobsListResponse)
def get_scheduler_jobs(request: Request):
    scheduler = getattr(request.app.state, "scheduler", None)
    service = SchedulerService()
    items = service.list_jobs(scheduler)

    return {
        "items": items,
        "count": len(items),
    }


@router.post("/admin/scheduler/pause", response_model=SchedulerControlResponse)
def pause_scheduler(request: Request):
    scheduler = getattr(request.app.state, "scheduler", None)
    service = SchedulerService()

    try:
        return service.pause_scheduler(scheduler)
    except ValueError as exc:
        if str(exc) == "SCHEDULER_DISABLED":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "SCHEDULER_DISABLED",
                    "message": "scheduler is disabled",
                },
            )
        if str(exc) == "SCHEDULER_NOT_RUNNING":
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "SCHEDULER_NOT_RUNNING",
                    "message": "scheduler is not running",
                },
            )
        raise


@router.post("/admin/scheduler/resume", response_model=SchedulerControlResponse)
def resume_scheduler(request: Request):
    scheduler = getattr(request.app.state, "scheduler", None)
    service = SchedulerService()

    try:
        return service.resume_scheduler(scheduler)
    except ValueError as exc:
        if str(exc) == "SCHEDULER_DISABLED":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "SCHEDULER_DISABLED",
                    "message": "scheduler is disabled",
                },
            )
        if str(exc) == "SCHEDULER_NOT_RUNNING":
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "SCHEDULER_NOT_RUNNING",
                    "message": "scheduler is not running",
                },
            )
        raise


@router.post("/admin/scheduler/jobs/{job_id}/pause", response_model=SchedulerControlResponse)
def pause_scheduler_job(job_id: str, request: Request):
    scheduler = getattr(request.app.state, "scheduler", None)
    service = SchedulerService()

    try:
        return service.pause_job(scheduler, job_id)
    except ValueError as exc:
        if str(exc) == "SCHEDULER_DISABLED":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "SCHEDULER_DISABLED",
                    "message": "scheduler is disabled",
                },
            )
        if str(exc) == "SCHEDULER_NOT_RUNNING":
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "SCHEDULER_NOT_RUNNING",
                    "message": "scheduler is not running",
                },
            )
        if str(exc) == "SCHEDULER_JOB_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "SCHEDULER_JOB_NOT_FOUND",
                    "message": "job not found",
                },
            )
        raise


@router.post("/admin/scheduler/jobs/{job_id}/resume", response_model=SchedulerControlResponse)
def resume_scheduler_job(job_id: str, request: Request):
    scheduler = getattr(request.app.state, "scheduler", None)
    service = SchedulerService()

    try:
        return service.resume_job(scheduler, job_id)
    except ValueError as exc:
        if str(exc) == "SCHEDULER_DISABLED":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "SCHEDULER_DISABLED",
                    "message": "scheduler is disabled",
                },
            )
        if str(exc) == "SCHEDULER_NOT_RUNNING":
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "SCHEDULER_NOT_RUNNING",
                    "message": "scheduler is not running",
                },
            )
        if str(exc) == "SCHEDULER_JOB_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "SCHEDULER_JOB_NOT_FOUND",
                    "message": "job not found",
                },
            )
        raise


@router.post("/admin/scheduler/jobs/{job_id}/run-now", response_model=SchedulerRunNowResponse)
def run_scheduler_job_now(job_id: str, request: Request):
    scheduler = getattr(request.app.state, "scheduler", None)
    service = SchedulerService()

    try:
        return service.run_job_now(scheduler, job_id)
    except ValueError as exc:
        if str(exc) == "SCHEDULER_DISABLED":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "SCHEDULER_DISABLED",
                    "message": "scheduler is disabled",
                },
            )
        if str(exc) == "SCHEDULER_NOT_RUNNING":
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "SCHEDULER_NOT_RUNNING",
                    "message": "scheduler is not running",
                },
            )
        if str(exc) == "SCHEDULER_JOB_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "SCHEDULER_JOB_NOT_FOUND",
                    "message": "job not found",
                },
            )
        raise
