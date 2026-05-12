import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import type { MarketType, StockSearchItem } from "../types/stock";
import { searchStocks } from "../services/stockApi";
import StockSearchToolbar from "../components/StockSearchToolbar";
import StockSearchResultList from "../components/StockSearchResultList";

type MarketFilter = "ALL" | MarketType;

function isValidMarket(value: string | null): value is MarketType {
  return value === "TWSE" || value === "TPEX";
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

export default function StocksPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [keyword, setKeyword] = useState("");
  const [market, setMarket] = useState<MarketFilter>("ALL");
  const [items, setItems] = useState<StockSearchItem[]>([]);
  const [count, setCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  const runSearch = async (params: {
    keyword: string;
    market: MarketFilter;
    page: number;
    pageSize: number;
  }) => {
    const trimmedKeyword = params.keyword.trim();

    if (!trimmedKeyword) {
      setItems([]);
      setCount(0);
      setTotalCount(0);
      setError(null);
      setHasSearched(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await searchStocks({
        q: trimmedKeyword,
        market: params.market === "ALL" ? undefined : params.market,
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
    const qFromUrl = searchParams.get("q") ?? "";
    const marketFromUrl = searchParams.get("market");
    const pageFromUrl = searchParams.get("page");
    const pageSizeFromUrl = searchParams.get("page_size");

    const parsedMarket: MarketFilter = isValidMarket(marketFromUrl)
      ? marketFromUrl
      : "ALL";

    const parsedPage = parsePositiveInt(pageFromUrl, 1);
    const parsedPageSize = normalizePageSize(pageSizeFromUrl);

    setKeyword(qFromUrl);
    setMarket(parsedMarket);
    setPage(parsedPage);
    setPageSize(parsedPageSize);

    if (qFromUrl.trim()) {
      void runSearch({
        keyword: qFromUrl,
        market: parsedMarket,
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

    const trimmedKeyword = keyword.trim();
    if (trimmedKeyword) {
      nextParams.set("q", trimmedKeyword);
    }

    if (market !== "ALL") {
      nextParams.set("market", market);
    }

    nextParams.set("page", String(options?.nextPage ?? page));
    nextParams.set("page_size", String(options?.nextPageSize ?? pageSize));

    return nextParams;
  };

  const handleSearch = async () => {
    const trimmedKeyword = keyword.trim();

    if (!trimmedKeyword) {
      setError("請輸入搜尋關鍵字");
      setItems([]);
      setCount(0);
      setTotalCount(0);
      setHasSearched(false);
      return;
    }

    const nextParams = buildSearchParams({
      nextPage: 1,
      nextPageSize: pageSize,
    });

    setSearchParams(nextParams);
  };

  const handleReset = () => {
    setKeyword("");
    setMarket("ALL");
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

  const handleViewDividends = (item: StockSearchItem) => {
    navigate(`/stocks/${item.stock_code}/dividends?market=${item.market}`);
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
            股票搜尋
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
            可依股票代號、公司名稱、公司簡稱搜尋 TWSE / TPEX 股票
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
          <StockSearchToolbar
            keyword={keyword}
            market={market}
            loading={loading}
            onKeywordChange={setKeyword}
            onMarketChange={setMarket}
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
              : "尚未搜尋"}
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
          </div>
        </div>

        <StockSearchResultList
          items={items}
          loading={loading}
          error={error}
          hasSearched={hasSearched}
          onViewDividends={handleViewDividends}
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