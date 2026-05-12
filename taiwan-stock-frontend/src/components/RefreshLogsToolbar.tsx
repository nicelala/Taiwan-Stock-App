import type { CSSProperties } from "react";
import type {
  RefreshJobName,
  RefreshMarket,
  RefreshStatus,
} from "../types/admin";

type JobFilter = "ALL" | RefreshJobName;
type MarketFilter = "ALL" | RefreshMarket;
type StatusFilter = "ALL" | RefreshStatus;

type RefreshLogsToolbarProps = {
  jobName: JobFilter;
  market: MarketFilter;
  status: StatusFilter;
  loading: boolean;
  onJobNameChange: (value: JobFilter) => void;
  onMarketChange: (value: MarketFilter) => void;
  onStatusChange: (value: StatusFilter) => void;
  onSearch: () => void;
  onReset: () => void;
};

export default function RefreshLogsToolbar({
  jobName,
  market,
  status,
  loading,
  onJobNameChange,
  onMarketChange,
  onStatusChange,
  onSearch,
  onReset,
}: RefreshLogsToolbarProps) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "220px 180px 180px 120px 120px",
        gap: "12px",
        marginBottom: "20px",
      }}
    >
      <select
        value={jobName}
        onChange={(e) => onJobNameChange(e.target.value as JobFilter)}
        style={inputStyle}
        disabled={loading}
      >
        <option value="ALL">全部工作</option>
        <option value="refresh_stocks">refresh_stocks</option>
        <option value="refresh_dividends">refresh_dividends</option>
      </select>

      <select
        value={market}
        onChange={(e) => onMarketChange(e.target.value as MarketFilter)}
        style={inputStyle}
        disabled={loading}
      >
        <option value="ALL">全部市場</option>
        <option value="TWSE">TWSE</option>
        <option value="TPEX">TPEX</option>
      </select>

      <select
        value={status}
        onChange={(e) => onStatusChange(e.target.value as StatusFilter)}
        style={inputStyle}
        disabled={loading}
      >
        <option value="ALL">全部狀態</option>
        <option value="success">success</option>
        <option value="failed">failed</option>
        <option value="running">running</option>
      </select>

      <button onClick={onSearch} disabled={loading} style={primaryButtonStyle}>
        {loading ? "查詢中..." : "查詢"}
      </button>

      <button onClick={onReset} disabled={loading} style={secondaryButtonStyle}>
        重設
      </button>
    </div>
  );
}

const inputStyle: CSSProperties = {
  width: "100%",
  height: "42px",
  padding: "0 12px",
  borderRadius: "12px",
  border: "1px solid #cbd5e1",
  outline: "none",
  fontSize: "14px",
  backgroundColor: "#fff",
};

const primaryButtonStyle: CSSProperties = {
  height: "42px",
  borderRadius: "12px",
  border: "none",
  backgroundColor: "#0f172a",
  color: "#fff",
  fontSize: "14px",
  cursor: "pointer",
};

const secondaryButtonStyle: CSSProperties = {
  height: "42px",
  borderRadius: "12px",
  border: "1px solid #cbd5e1",
  backgroundColor: "#fff",
  color: "#0f172a",
  fontSize: "14px",
  cursor: "pointer",
};