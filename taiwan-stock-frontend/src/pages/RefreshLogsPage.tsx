import { useEffect, useState } from "react";
import type {
  RefreshJobName,
  RefreshLogItem,
  RefreshMarket,
  RefreshStatus,
} from "../types/admin";
import { getRefreshLogs } from "../services/adminApi";
import RefreshLogsToolbar from "../components/RefreshLogsToolbar";
import RefreshLogsTable from "../components/RefreshLogsTable";

type JobFilter = "ALL" | RefreshJobName;
type MarketFilter = "ALL" | RefreshMarket;
type StatusFilter = "ALL" | RefreshStatus;

export default function RefreshLogsPage() {
  const [jobName, setJobName] = useState<JobFilter>("ALL");
  const [market, setMarket] = useState<MarketFilter>("ALL");
  const [status, setStatus] = useState<StatusFilter>("ALL");

  const [items, setItems] = useState<RefreshLogItem[]>([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasLoaded, setHasLoaded] = useState(false);

  const [limit] = useState(20);
  const [offset, setOffset] = useState(0);

  const pageNumber = Math.floor(offset / limit) + 1;
  const hasNextPage = count === limit;
  const hasPrevPage = offset > 0;

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

  const handleExportRefreshLogsCsv = () => {
    const params = new URLSearchParams();

    // 依目前頁面 filter 狀態帶參數（忽略分頁 limit/offset）
    if (jobName !== "ALL") params.set("job_name", jobName);
    if (market !== "ALL") params.set("market", market);
    if (status !== "ALL") params.set("status", status);

    params.set("format", "csv");

    const url = `${API_BASE_URL}/api/v1/admin/refresh/logs/export?${params.toString()}`;
    triggerDownload(url);
  };


  const loadLogs = async (nextOffset: number) => {
    setLoading(true);
    setError(null);

    try {
      const result = await getRefreshLogs({
        job_name: jobName === "ALL" ? undefined : jobName,
        market: market === "ALL" ? undefined : market,
        status: status === "ALL" ? undefined : status,
        limit,
        offset: nextOffset,
      });

      setItems(result.items);
      setCount(result.count);
      setOffset(nextOffset);
      setHasLoaded(true);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "查詢失敗，請稍後再試。";
      setError(message);
      setItems([]);
      setCount(0);
      setHasLoaded(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadLogs(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSearch = async () => {
    await loadLogs(0);
  };

  const handleReset = async () => {
    setJobName("ALL");
    setMarket("ALL");
    setStatus("ALL");
    setItems([]);
    setCount(0);
    setError(null);
    setHasLoaded(false);

    setTimeout(() => {
      void loadLogs(0);
    }, 0);
  };

  const handlePrevPage = async () => {
    if (!hasPrevPage || loading) return;
    await loadLogs(offset - limit);
  };

  const handleNextPage = async () => {
    if (!hasNextPage || loading) return;
    await loadLogs(offset + limit);
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
          maxWidth: "1400px",
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
            Refresh Logs
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
            查看股票 / 股利 refresh 歷史紀錄與執行結果
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
          <RefreshLogsToolbar
            jobName={jobName}
            market={market}
            status={status}
            loading={loading}
            onJobNameChange={setJobName}
            onMarketChange={setMarket}
            onStatusChange={setStatus}
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
            {hasLoaded && !loading
              ? `目前第 ${pageNumber} 批，這批共 ${count} 筆`
              : "尚未載入"}
          </div>

          <div
            style={{
              display: "flex",
              gap: "12px",
            }}
          >
            <button
              onClick={handlePrevPage}
              disabled={loading || !hasPrevPage}
              style={secondaryButtonStyle}
            >
              上一頁
            </button>

            <button
              onClick={handleNextPage}
              disabled={loading || !hasNextPage}
              style={primaryButtonStyle}
            >
              下一頁
            </button>

            <button
            type="button"
            onClick={handleExportRefreshLogsCsv}
            disabled={loading}
            style={secondaryButtonStyle}
          >
            匯出 CSV
          </button>
          </div>
        </div>

        <RefreshLogsTable
          items={items}
          loading={loading}
          error={error}
          hasLoaded={hasLoaded}
        />
      </div>
    </div>
  );
}

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

