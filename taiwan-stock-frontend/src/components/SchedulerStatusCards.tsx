import type { CSSProperties } from "react";
import type { SchedulerStatusResponse } from "../types/scheduler";

type SchedulerStatusCardsProps = {
  statusInfo: SchedulerStatusResponse | null;
  loading: boolean;
};

export default function SchedulerStatusCards({
  statusInfo,
  loading,
}: SchedulerStatusCardsProps) {
  if (loading) {
    return <div style={infoBoxStyle}>載入 scheduler 狀態中...</div>;
  }

  if (!statusInfo) {
    return <div style={infoBoxStyle}>尚未取得 scheduler 狀態</div>;
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
        gap: "16px",
      }}
    >
      <div style={cardStyle}>
        <div style={labelStyle}>Enabled</div>
        <div style={valueStyle}>{String(statusInfo.enabled)}</div>
      </div>

      <div style={cardStyle}>
        <div style={labelStyle}>Running</div>
        <div style={valueStyle}>{String(statusInfo.running)}</div>
      </div>

      <div style={cardStyle}>
        <div style={labelStyle}>Job Count</div>
        <div style={valueStyle}>{statusInfo.job_count}</div>
      </div>
    </div>
  );
}

const infoBoxStyle: CSSProperties = {
  border: "1px solid #e2e8f0",
  backgroundColor: "#fff",
  borderRadius: "18px",
  padding: "20px",
  color: "#475569",
};

const cardStyle: CSSProperties = {
  border: "1px solid #e2e8f0",
  borderRadius: "18px",
  backgroundColor: "#fff",
  padding: "20px",
  boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
};

const labelStyle: CSSProperties = {
  color: "#64748b",
  fontSize: "13px",
  marginBottom: "8px",
};

const valueStyle: CSSProperties = {
  color: "#0f172a",
  fontSize: "28px",
  fontWeight: 800,
};