import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import type {
  MarketType,
  SortByType,
  SortDirType,
  DividendSearchItem,
} from "../types/dividend";
import { searchDividends } from "../services/dividendApi";
import DividendSearchToolbar from "../components/DividendSearchToolbar";
import DividendSearchResultList from "../components/DividendSearchResultList";

type MarketFilter = "ALL" | MarketType;

function isValidMarket(value: string | null): value is MarketType {
  return value === "TWSE" || value === "TPEX";
}

function isValidSortBy(value: string | null): value is SortByType {
  return value === "cash" || value === "stock" || value === "total" || value === "year" || value === "code";
}

function isValidSortDir(value: string | null): value is SortDirType {
  return value === "asc" || value === "desc";
}

function parsePositiveInt(value: string | null, fallback: number): number {
  if (!value) return fallback;

  const parsed = Number(value);
  if (Number.isNaN(parsed) || parsed < 1) return fallback;

  return Math.floor(parsed);
}

function normalizePageSize(value: string | null): number {
  const parsed = parsePositiveInt(value, 20);
  if (parsed === 20 || parsed === 50 || parsed === 100) return parsed;
  return 20;
}

export default function DividendsPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const [market, setMarket] = useState<MarketFilter>("ALL");
  const [year, setYear] = useState("");
  const [cashMin, setCashMin] = useState("");
  const [stockMin, setStockMin] = useState("");
  const [totalMin, setTotalMin] = useState("");
  const [sortBy, setSortBy] = useState<SortByType>("total");
  const [sortDir, setSortDir] = useState<SortDirType>("desc");

  const [items, setItems] = useState<DividendSearchItem[]>([]);
  const [count, setCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

  
  const triggerDownload = (url: string) => {
    const a = document.createElement("a");
    a.href = url;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    document.body.appendChild(a);
    a.click();
    a.remove();
  };


  const buildDividendsExportUrl = (format: "csv" | "xlsx") => {
    const params = new URLSearchParams(searchParams);

    // 匯出不吃分頁
    params.delete("page");
    params.delete("page_size");

    params.set("format", format);

    return `${API_BASE_URL}/api/v1/dividends/export?${params.toString()}`;
  };

  const handleExportDividendsCsv = () => {
    triggerDownload(buildDividendsExportUrl("csv"));
  };

  const handleExportDividendsXlsx = () => {
    triggerDownload(buildDividendsExportUrl("xlsx"));
  };

  const parseOptionalNumber = (value: string): number | undefined => {
    const trimmed = value.trim();
    if (!trimmed) return undefined;

    const num = Number(trimmed);
    if (Number.isNaN(num)) return undefined;

    return num;
  };

  const loadDividends = async (params: {
    market: MarketFilter;
    year: string;
    cashMin: string;
    stockMin: string;
    totalMin: string;
    sortBy: SortByType;
    sortDir: SortDirType;
    page: number;
    pageSize: number;
  }) => {
    setLoading(true);
    setError(null);

    try {
      const result = await searchDividends({
        market: params.market === "ALL" ? undefined : params.market,
        year: parseOptionalNumber(params.year),
        cash_min: parseOptionalNumber(params.cashMin),
        stock_min: parseOptionalNumber(params.stockMin),
        total_min: parseOptionalNumber(params.totalMin),
        sort_by: params.sortBy,
        sort_dir: params.sortDir,
        limit: params.pageSize,
        offset: (params.page - 1) * params.pageSize,
      });

      setItems(result.items);
      setCount(result.count);
      setTotalCount(result.total_count);
      setHasSearched(true);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "查詢失敗，請稍後再試。";
      setError(message);
      setItems([]);
      setCount(0);
      setTotalCount(0);
      setHasSearched(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const marketFromUrl = searchParams.get("market");
    const yearFromUrl = searchParams.get("year") ?? "";
    const cashMinFromUrl = searchParams.get("cash_min") ?? "";
    const stockMinFromUrl = searchParams.get("stock_min") ?? "";
    const totalMinFromUrl = searchParams.get("total_min") ?? "";
    const sortByFromUrl = searchParams.get("sort_by");
    const sortDirFromUrl = searchParams.get("sort_dir");
    const pageFromUrl = searchParams.get("page");
    const pageSizeFromUrl = searchParams.get("page_size");

    const parsedMarket: MarketFilter = isValidMarket(marketFromUrl)
      ? marketFromUrl
      : "ALL";

    const parsedSortBy: SortByType = isValidSortBy(sortByFromUrl)
      ? sortByFromUrl
      : "total";

    const parsedSortDir: SortDirType = isValidSortDir(sortDirFromUrl)
      ? sortDirFromUrl
      : "desc";

    const parsedPage = parsePositiveInt(pageFromUrl, 1);
    const parsedPageSize = normalizePageSize(pageSizeFromUrl);

    setMarket(parsedMarket);
    setYear(yearFromUrl);
    setCashMin(cashMinFromUrl);
    setStockMin(stockMinFromUrl);
    setTotalMin(totalMinFromUrl);
    setSortBy(parsedSortBy);
    setSortDir(parsedSortDir);
    setPage(parsedPage);
    setPageSize(parsedPageSize);

    const hasAnyQuery =
      !!marketFromUrl ||
      !!yearFromUrl ||
      !!cashMinFromUrl ||
      !!stockMinFromUrl ||
      !!totalMinFromUrl ||
      !!sortByFromUrl ||
      !!sortDirFromUrl ||
      !!pageFromUrl ||
      !!pageSizeFromUrl;

    if (hasAnyQuery) {
      void loadDividends({
        market: parsedMarket,
        year: yearFromUrl,
        cashMin: cashMinFromUrl,
        stockMin: stockMinFromUrl,
        totalMin: totalMinFromUrl,
        sortBy: parsedSortBy,
        sortDir: parsedSortDir,
        page: parsedPage,
        pageSize: parsedPageSize,
      });
    } else {
      setItems([]);
      setCount(0);
      setTotalCount(0);
      setError(null);
      setHasSearched(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const buildSearchParams = (options?: {
    nextPage?: number;
    nextPageSize?: number;
  }) => {
    const nextParams = new URLSearchParams();

    if (market !== "ALL") nextParams.set("market", market);
    if (year.trim()) nextParams.set("year", year.trim());
    if (cashMin.trim()) nextParams.set("cash_min", cashMin.trim());
    if (stockMin.trim()) nextParams.set("stock_min", stockMin.trim());
    if (totalMin.trim()) nextParams.set("total_min", totalMin.trim());

    nextParams.set("sort_by", sortBy);
    nextParams.set("sort_dir", sortDir);
    nextParams.set("page", String(options?.nextPage ?? page));
    nextParams.set("page_size", String(options?.nextPageSize ?? pageSize));

    return nextParams;
  };

  const handleSearch = async () => {
    const nextParams = buildSearchParams({
      nextPage: 1,
      nextPageSize: pageSize,
    });

    setSearchParams(nextParams);
  };

  const handleReset = () => {
    setMarket("ALL");
    setYear("");
    setCashMin("");
    setStockMin("");
    setTotalMin("");
    setSortBy("total");
    setSortDir("desc");
    setItems([]);
    setCount(0);
    setTotalCount(0);
    setError(null);
    setHasSearched(false);
    setPage(1);
    setPageSize(20);
    setSearchParams({});
  };

  const handlePrevPage = async () => {
    if (page <= 1 || loading) return;

    const nextParams = buildSearchParams({
      nextPage: page - 1,
      nextPageSize: pageSize,
    });

    setSearchParams(nextParams);
  };

  const handleNextPage = async () => {
    if (page >= totalPages || loading) return;

    const nextParams = buildSearchParams({
      nextPage: page + 1,
      nextPageSize: pageSize,
    });

    setSearchParams(nextParams);
  };

  const handlePageSizeChange = async (value: number) => {
    const nextParams = buildSearchParams({
      nextPage: 1,
      nextPageSize: value,
    });

    setSearchParams(nextParams);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#f8fafc",
        padding: "24px",
      }}
    >
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
        }}
      >
        <div
          style={{
            marginBottom: "24px",
            padding: "20px",
            borderRadius: "20px",
            backgroundColor: "#fff",
            border: "1px solid #e2e8f0",
            boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
          }}
        >
          <h1
            style={{
              fontSize: "28px",
              fontWeight: 800,
              margin: 0,
              color: "#0f172a",
            }}
          >
            股利篩選 / 排行
          </h1>
          <p
            style={{
              marginTop: "8px",
              marginBottom: 0,
              color: "#64748b",
              fontSize: "14px",
              lineHeight: 1.6,
            }}
          >
            可依市場、年度、股利門檻與排序條件篩選股利資料
          </p>
        </div>

        <div
          style={{
            marginBottom: "20px",
            padding: "20px",
            borderRadius: "20px",
            backgroundColor: "#fff",
            border: "1px solid #e2e8f0",
            boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
          }}
        >
          <DividendSearchToolbar
            market={market}
            year={year}
            cashMin={cashMin}
            stockMin={stockMin}
            totalMin={totalMin}
            sortBy={sortBy}
            sortDir={sortDir}
            loading={loading}
            onMarketChange={setMarket}
            onYearChange={setYear}
            onCashMinChange={setCashMin}
            onStockMinChange={setStockMin}
            onTotalMinChange={setTotalMin}
            onSortByChange={setSortBy}
            onSortDirChange={setSortDir}
            onSearch={handleSearch}
            onReset={handleReset}
          />
        </div>

        <div
          style={{
            marginBottom: "16px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "16px",
            flexWrap: "wrap",
            color: "#475569",
            fontSize: "14px",
          }}
        >
          <div>
            {hasSearched && !loading
              ? `找到 ${count} 筆結果（總共 ${totalCount} 筆，頁面 ${page} / ${totalPages}）`
              : "尚未查詢"}
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              flexWrap: "wrap",
            }}
          >
            <span>每頁筆數</span>

            <select
              value={pageSize}
              onChange={(e) => handlePageSizeChange(Number(e.target.value))}
              disabled={loading}
              style={selectStyle}
            >
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>

            <button
              onClick={handlePrevPage}
              disabled={loading || page <= 1}
              style={secondaryButtonStyle}
            >
              上一頁
            </button>

            <button
              onClick={handleNextPage}
              disabled={loading || page >= totalPages}
              style={primaryButtonStyle}
            >
              下一頁
            </button>

            <button
              onClick={handleExportDividendsCsv}
              disabled={!hasSearched || loading}
              style={secondaryButtonStyle}
            >
              匯出 CSV
            </button>

            <button
              onClick={handleExportDividendsXlsx}
              disabled={!hasSearched || loading}
              style={primaryButtonStyle}
            >
              匯出 Excel
            </button>
          </div>
        </div>

        <DividendSearchResultList
          items={items}
          loading={loading}
          error={error}
          hasSearched={hasSearched}
        />
      </div>
    </div>
  );
}

const selectStyle: React.CSSProperties = {
  height: "38px",
  borderRadius: "12px",
  border: "1px solid #cbd5e1",
  padding: "0 12px",
  backgroundColor: "#fff",
};

const primaryButtonStyle: React.CSSProperties = {
  height: "38px",
  borderRadius: "12px",
  border: "none",
  backgroundColor: "#0f172a",
  color: "#fff",
  fontSize: "14px",
  cursor: "pointer",
  padding: "0 16px",
};

const secondaryButtonStyle: React.CSSProperties = {
  height: "38px",
  borderRadius: "12px",
  border: "1px solid #cbd5e1",
  backgroundColor: "#fff",
  color: "#0f172a",
  fontSize: "14px",
  cursor: "pointer",
  padding: "0 16px",
};