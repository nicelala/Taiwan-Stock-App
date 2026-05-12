import type { CSSProperties } from "react";
import type { SchedulerJobItem } from "../types/scheduler";

type ActionType = "pause" | "resume" | "run-now";

type SchedulerJobCardProps = {
  job: SchedulerJobItem;
  actionLoadingKey: string | null;
  onPause: (jobId: string) => void;
  onResume: (jobId: string) => void;
  onRunNow: (jobId: string) => void;
};

export default function SchedulerJobCard({
  job,
  actionLoadingKey,
  onPause,
  onResume,
  onRunNow,
}: SchedulerJobCardProps) {
  const isPauseLoading = actionLoadingKey === `${job.id}:pause`;
  const isResumeLoading = actionLoadingKey === `${job.id}:resume`;
  const isRunNowLoading = actionLoadingKey === `${job.id}:run-now`;

  return (
    <div
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
          <div style={{ fontSize: "18px", fontWeight: 700, color: "#0f172a" }}>
            {job.id}
          </div>
          <div style={{ fontSize: "14px", color: "#64748b", marginTop: "4px" }}>
            {job.name}
          </div>
        </div>

        <span style={job.paused ? pausedBadgeStyle : runningBadgeStyle}>
          {job.paused ? "paused" : "running"}
        </span>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
          gap: "12px",
          marginTop: "16px",
          fontSize: "14px",
        }}
      >
        <div>
          <div style={labelStyle}>Args</div>
          <div>{job.args.length > 0 ? job.args.join(", ") : "-"}</div>
        </div>

        <div>
          <div style={labelStyle}>Trigger</div>
          <div>{job.trigger}</div>
        </div>

        <div>
          <div style={labelStyle}>Next Run Time</div>
          <div>{job.next_run_time ?? "-"}</div>
        </div>
      </div>

      <div
        style={{
          display: "flex",
          gap: "12px",
          flexWrap: "wrap",
          marginTop: "16px",
        }}
      >
        <ActionButton
          text={isPauseLoading ? "Pause 中..." : "Pause"}
          disabled={isPauseLoading || isResumeLoading || isRunNowLoading}
          primary={false}
          onClick={() => onPause(job.id)}
        />

        <ActionButton
          text={isResumeLoading ? "Resume 中..." : "Resume"}
          disabled={isPauseLoading || isResumeLoading || isRunNowLoading}
          primary={false}
          onClick={() => onResume(job.id)}
        />

        <ActionButton
          text={isRunNowLoading ? "Run Now 中..." : "Run Now"}
          disabled={isPauseLoading || isResumeLoading || isRunNowLoading}
          primary={true}
          onClick={() => onRunNow(job.id)}
        />
      </div>
    </div>
  );
}

function ActionButton({
  text,
  disabled,
  primary,
  onClick,
}: {
  text: string;
  disabled: boolean;
  primary: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={primary ? primaryButtonStyle : secondaryButtonStyle}
    >
      {text}
    </button>
  );
}

const labelStyle: CSSProperties = {
  color: "#64748b",
  fontSize: "12px",
  marginBottom: "4px",
};

const primaryButtonStyle: CSSProperties = {
  height: "38px",
  borderRadius: "12px",
  border: "none",
  backgroundColor: "#0f172a",
  color: "#fff",
  fontSize: "14px",
  cursor: "pointer",
  padding: "0 16px",
};

const secondaryButtonStyle: CSSProperties = {
  height: "38px",
  borderRadius: "12px",
  border: "1px solid #cbd5e1",
  backgroundColor: "#fff",
  color: "#0f172a",
  fontSize: "14px",
  cursor: "pointer",
  padding: "0 16px",
};

const pausedBadgeStyle: CSSProperties = {
  backgroundColor: "#fef3c7",
  color: "#b45309",
  border: "1px solid #fde68a",
  borderRadius: "999px",
  padding: "4px 10px",
  fontSize: "12px",
  fontWeight: 600,
  whiteSpace: "nowrap",
};

const runningBadgeStyle: CSSProperties = {
  backgroundColor: "#d1fae5",
  color: "#047857",
  border: "1px solid #a7f3d0",
  borderRadius: "999px",
  padding: "4px 10px",
  fontSize: "12px",
  fontWeight: 600,
  whiteSpace: "nowrap",
};