import type { CSSProperties } from "react";
import type { RefreshLogItem } from "../types/admin";

type RefreshLogsTableProps = {
  items: RefreshLogItem[];
  loading: boolean;
  error: string | null;
  hasLoaded: boolean;
};

export default function RefreshLogsTable({
  items,
  loading,
  error,
  hasLoaded,
}: RefreshLogsTableProps) {
  if (loading) {
    return <div style={infoBoxStyle}>載入中，請稍候...</div>;
  }

  if (error) {
    return (
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
    );
  }

  if (!hasLoaded) {
    return <div style={infoBoxStyle}>尚未載入 refresh logs</div>;
  }

  if (items.length === 0) {
    return <div style={infoBoxStyle}>查無符合條件的 refresh logs</div>;
  }

  return (
    <div
      style={{
        overflowX: "auto",
        borderRadius: "18px",
        border: "1px solid #e2e8f0",
        backgroundColor: "#fff",
      }}
    >
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          minWidth: "1200px",
        }}
      >
        <thead>
          <tr style={{ backgroundColor: "#f8fafc" }}>
            <th style={thStyle}>ID</th>
            <th style={thStyle}>Job</th>
            <th style={thStyle}>Market</th>
            <th style={thStyle}>Status</th>
            <th style={thStyle}>Trigger</th>
            <th style={thStyle}>Started</th>
            <th style={thStyle}>Finished</th>
            <th style={thStyle}>Duration (ms)</th>
            <th style={thStyle}>Inserted/Updated</th>
            <th style={thStyle}>Skipped</th>
            <th style={thStyle}>Error</th>
          </tr>
        </thead>

        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td style={tdStyle}>{item.id}</td>
              <td style={tdStyle}>{item.job_name}</td>
              <td style={tdStyle}>
                <span style={marketBadgeStyle(item.market)}>{item.market}</span>
              </td>
              <td style={tdStyle}>
                <span style={statusBadgeStyle(item.status)}>{item.status}</span>
              </td>
              <td style={tdStyle}>{item.trigger_source}</td>
              <td style={tdStyle}>{item.started_at}</td>
              <td style={tdStyle}>{item.finished_at ?? "-"}</td>
              <td style={tdStyle}>{item.duration_ms ?? "-"}</td>
              <td style={tdStyle}>{item.inserted_or_updated_count ?? "-"}</td>
              <td style={tdStyle}>{item.skipped_count ?? "-"}</td>
              <td style={tdStyle}>
                <div
                  title={item.error_message ?? ""}
                  style={{
                    maxWidth: "280px",
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                >
                  {item.error_message ?? "-"}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const thStyle: CSSProperties = {
  textAlign: "left",
  padding: "12px",
  fontSize: "13px",
  color: "#334155",
  borderBottom: "1px solid #e2e8f0",
};

const tdStyle: CSSProperties = {
  padding: "12px",
  fontSize: "14px",
  color: "#0f172a",
  borderBottom: "1px solid #f1f5f9",
  verticalAlign: "top",
};

const infoBoxStyle: CSSProperties = {
  border: "1px solid #e2e8f0",
  backgroundColor: "#fff",
  borderRadius: "18px",
  padding: "20px",
  color: "#475569",
};

function marketBadgeStyle(market: string): CSSProperties {
  if (market === "TWSE") {
    return {
      backgroundColor: "#dbeafe",
      color: "#1d4ed8",
      border: "1px solid #bfdbfe",
      borderRadius: "999px",
      padding: "4px 10px",
      fontSize: "12px",
      fontWeight: 600,
      whiteSpace: "nowrap",
    };
  }

  return {
    backgroundColor: "#d1fae5",
    color: "#047857",
    border: "1px solid #a7f3d0",
    borderRadius: "999px",
    padding: "4px 10px",
    fontSize: "12px",
    fontWeight: 600,
    whiteSpace: "nowrap",
  };
}

function statusBadgeStyle(status: string): CSSProperties {
  if (status === "success") {
    return {
      backgroundColor: "#d1fae5",
      color: "#047857",
      border: "1px solid #a7f3d0",
      borderRadius: "999px",
      padding: "4px 10px",
      fontSize: "12px",
      fontWeight: 600,
      whiteSpace: "nowrap",
    };
  }

  if (status === "failed") {
    return {
      backgroundColor: "#fee2e2",
      color: "#b91c1c",
      border: "1px solid #fecaca",
      borderRadius: "999px",
      padding: "4px 10px",
      fontSize: "12px",
      fontWeight: 600,
      whiteSpace: "nowrap",
    };
  }

  return {
    backgroundColor: "#fef3c7",
    color: "#b45309",
    border: "1px solid #fde68a",
    borderRadius: "999px",
    padding: "4px 10px",
    fontSize: "12px",
    fontWeight: 600,
    whiteSpace: "nowrap",
  };
}