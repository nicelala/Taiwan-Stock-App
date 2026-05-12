import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { getStockDividends } from "../services/dividendApi";
import type { MarketType, StockDividendItem } from "../types/dividend";

export default function StockDividendsPage() {
  const navigate = useNavigate();
  const { stockCode = "" } = useParams<{ stockCode: string }>();
  const [searchParams] = useSearchParams();

  const market = (searchParams.get("market") || undefined) as MarketType | undefined;

  const [yearFrom, setYearFrom] = useState("");
  const [yearTo, setYearTo] = useState("");
  const [items, setItems] = useState<StockDividendItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pageTitle = useMemo(() => {
    if (!stockCode) return "個股股利資料";
    return `${stockCode} 股利資料`;
  }, [stockCode]);

  const parseOptionalNumber = (value: string): number | undefined => {
    const trimmed = value.trim();
    if (!trimmed) return undefined;

    const num = Number(trimmed);
    if (Number.isNaN(num)) return undefined;

    return num;
  };

  const loadDividends = async (options?: {
    yearFrom?: number;
    yearTo?: number;
  }) => {
    if (!stockCode) {
      setError("缺少股票代號");
      setItems([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await getStockDividends({
        stockCode,
        market,
        yearFrom: options?.yearFrom,
        yearTo: options?.yearTo,
      });

      setItems(result.items);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "查詢失敗，請稍後再試。";
      setError(message);
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDividends();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stockCode, market]);

  const handleApplyFilter = async () => {
    await loadDividends({
      yearFrom: parseOptionalNumber(yearFrom),
      yearTo: parseOptionalNumber(yearTo),
    });
  };

  const handleReset = async () => {
    setYearFrom("");
    setYearTo("");
    await loadDividends();
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
            display: "flex",
            justifyContent: "space-between",
            gap: "16px",
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <div
            style={{
              padding: "20px",
              borderRadius: "20px",
              backgroundColor: "#fff",
              border: "1px solid #e2e8f0",
              boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
              flex: 1,
              minWidth: "320px",
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
              {pageTitle}
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
              市場：{market ?? "未指定"}　/　查看單一股票的股利資料
            </p>
          </div>

          <button onClick={() => navigate("/stocks")} style={secondaryButtonStyle}>
            ← 返回股票搜尋
          </button>
        </div>

        <div
          style={{
            marginBottom: "20px",
            padding: "20px",
            borderRadius: "20px",
            backgroundColor: "#fff",
            border: "1px solid #e2e8f0",
            boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
            display: "grid",
            gridTemplateColumns: "220px 220px 140px 140px",
            gap: "12px",
            alignItems: "center",
          }}
        >
          <input
            type="text"
            value={yearFrom}
            onChange={(e) => setYearFrom(e.target.value)}
            placeholder="year_from（例如 113）"
            style={inputStyle}
            disabled={loading}
          />

          <input
            type="text"
            value={yearTo}
            onChange={(e) => setYearTo(e.target.value)}
            placeholder="year_to（例如 114）"
            style={inputStyle}
            disabled={loading}
          />

          <button onClick={handleApplyFilter} disabled={loading} style={primaryButtonStyle}>
            {loading ? "查詢中..." : "套用條件"}
          </button>

          <button onClick={handleReset} disabled={loading} style={secondaryButtonStyle}>
            重設
          </button>
        </div>

        {loading && <div style={infoBoxStyle}>查詢中，請稍候...</div>}

        {!loading && error && (
          <div
            style={{
              ...infoBoxStyle,
              border: "1px solid #fecaca",
              backgroundColor: "#fef2f2",
              color: "#b91c1c",
            }}
          >
            {error}
          </div>
        )}

        {!loading && !error && items.length === 0 && (
          <div style={infoBoxStyle}>查無股利資料</div>
        )}

        {!loading && !error && items.length > 0 && (
          <div
            style={{
              display: "grid",
              gap: "16px",
            }}
          >
            {items.map((item, index) => (
              <div
                key={`${item.dividend_year}-${item.period_label ?? "p"}-${index}`}
                style={{
                  border: "1px solid #e2e8f0",
                  borderRadius: "18px",
                  padding: "16px",
                  backgroundColor: "#fff",
                  boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: "12px",
                    alignItems: "flex-start",
                    flexWrap: "wrap",
                  }}
                >
                  <div>
                    <div style={{ fontSize: "18px", fontWeight: 700 }}>
                      {item.dividend_year} / {item.dividend_year_ad ?? "-"}
                    </div>
                    <div style={{ fontSize: "14px", color: "#64748b", marginTop: "4px" }}>
                      期別：{item.period_label ?? "-"}　|　決議狀態：{item.resolution_status ?? "-"}
                    </div>
                  </div>

                  <div
                    style={{
                      borderRadius: "999px",
                      padding: "4px 10px",
                      fontSize: "12px",
                      fontWeight: 600,
                      border: "1px solid #e2e8f0",
                      backgroundColor: "#fff",
                      color: "#334155",
                    }}
                  >
                    董事會日期：{item.board_approved_date ?? "-"}
                  </div>
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                    gap: "12px",
                    marginTop: "16px",
                    fontSize: "14px",
                  }}
                >
                  <div>
                    <div style={labelStyle}>現金股利</div>
                    <div>{item.cash_dividend_per_share ?? "-"}</div>
                  </div>

                  <div>
                    <div style={labelStyle}>股票股利</div>
                    <div>{item.stock_dividend_per_share ?? "-"}</div>
                  </div>

                  <div>
                    <div style={labelStyle}>總股利</div>
                    <div>{item.total_dividend_per_share ?? "-"}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  width: "100%",
  height: "42px",
  padding: "0 12px",
  borderRadius: "12px",
  border: "1px solid #cbd5e1",
  outline: "none",
  fontSize: "14px",
  backgroundColor: "#fff",
};

const primaryButtonStyle: React.CSSProperties = {
  height: "42px",
  borderRadius: "12px",
  border: "none",
  backgroundColor: "#0f172a",
  color: "#fff",
  fontSize: "14px",
  cursor: "pointer",
  padding: "0 16px",
};

const secondaryButtonStyle: React.CSSProperties = {
  height: "42px",
  borderRadius: "12px",
  border: "1px solid #cbd5e1",
  backgroundColor: "#fff",
  color: "#0f172a",
  fontSize: "14px",
  cursor: "pointer",
  padding: "0 16px",
};

const labelStyle: React.CSSProperties = {
  color: "#64748b",
  fontSize: "12px",
  marginBottom: "4px",
};

const infoBoxStyle: React.CSSProperties = {
  border: "1px solid #e2e8f0",
  backgroundColor: "#fff",
  borderRadius: "18px",
  padding: "20px",
  color: "#475569",
};