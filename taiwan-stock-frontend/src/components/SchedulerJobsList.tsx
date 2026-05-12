import type { CSSProperties } from "react";
import type { SchedulerJobItem } from "../types/scheduler";
import SchedulerJobCard from "./SchedulerJobCard";

type SchedulerJobsListProps = {
  jobs: SchedulerJobItem[];
  loading: boolean;
  error: string | null;
  hasLoaded: boolean;
  actionLoadingKey: string | null;
  onPauseJob: (jobId: string) => void;
  onResumeJob: (jobId: string) => void;
  onRunNowJob: (jobId: string) => void;
};

export default function SchedulerJobsList({
  jobs,
  loading,
  error,
  hasLoaded,
  actionLoadingKey,
  onPauseJob,
  onResumeJob,
  onRunNowJob,
}: SchedulerJobsListProps) {
  if (loading) {
    return <div style={infoBoxStyle}>載入 scheduler jobs 中...</div>;
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
    return <div style={infoBoxStyle}>尚未載入 scheduler jobs</div>;
  }

  if (jobs.length === 0) {
    return <div style={infoBoxStyle}>目前沒有 scheduler jobs</div>;
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))",
        gap: "16px",
      }}
    >
      {jobs.map((job) => (
        <SchedulerJobCard
          key={job.id}
          job={job}
          actionLoadingKey={actionLoadingKey}
          onPause={onPauseJob}
          onResume={onResumeJob}
          onRunNow={onRunNowJob}
        />
      ))}
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