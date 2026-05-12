import { useEffect, useState } from "react";
import {
  getSchedulerJobs,
  getSchedulerStatus,
  pauseScheduler,
  pauseSchedulerJob,
  resumeScheduler,
  resumeSchedulerJob,
  runSchedulerJobNow,
} from "../services/schedulerApi";
import type {
  SchedulerJobItem,
  SchedulerStatusResponse,
} from "../types/scheduler";
import SchedulerStatusCards from "../components/SchedulerStatusCards";
import SchedulerJobsList from "../components/SchedulerJobsList";

export default function SchedulerPage() {
  const [statusInfo, setStatusInfo] = useState<SchedulerStatusResponse | null>(null);
  const [jobs, setJobs] = useState<SchedulerJobItem[]>([]);

  const [loadingStatus, setLoadingStatus] = useState(false);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);

  const [pageError, setPageError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const [actionLoadingKey, setActionLoadingKey] = useState<string | null>(null);
  const [schedulerActionLoading, setSchedulerActionLoading] = useState<
    "pause" | "resume" | null
  >(null);

  const loadPage = async () => {
    setPageError(null);
    setLoadingStatus(true);
    setLoadingJobs(true);

    try {
      const [statusResult, jobsResult] = await Promise.all([
        getSchedulerStatus(),
        getSchedulerJobs(),
      ]);

      setStatusInfo(statusResult);
      setJobs(jobsResult.items);
      setHasLoaded(true);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "載入 scheduler 頁面失敗，請稍後再試。";
      setPageError(message);
      setHasLoaded(true);
    } finally {
      setLoadingStatus(false);
      setLoadingJobs(false);
    }
  };

  useEffect(() => {
    void loadPage();
  }, []);

  const refreshSchedulerData = async () => {
    try {
      const [statusResult, jobsResult] = await Promise.all([
        getSchedulerStatus(),
        getSchedulerJobs(),
      ]);

      setStatusInfo(statusResult);
      setJobs(jobsResult.items);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "重新整理 scheduler 資料失敗。";
      setActionError(message);
    }
  };

  const handlePauseScheduler = async () => {
    setActionError(null);
    setSuccessMessage(null);
    setSchedulerActionLoading("pause");

    try {
      await pauseScheduler();
      setSuccessMessage("Scheduler 已暫停");
      await refreshSchedulerData();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Pause scheduler 失敗。";
      setActionError(message);
    } finally {
      setSchedulerActionLoading(null);
    }
  };

  const handleResumeScheduler = async () => {
    setActionError(null);
    setSuccessMessage(null);
    setSchedulerActionLoading("resume");

    try {
      await resumeScheduler();
      setSuccessMessage("Scheduler 已恢復");
      await refreshSchedulerData();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Resume scheduler 失敗。";
      setActionError(message);
    } finally {
      setSchedulerActionLoading(null);
    }
  };

  const handlePauseJob = async (jobId: string) => {
    setActionError(null);
    setSuccessMessage(null);
    setActionLoadingKey(`${jobId}:pause`);

    try {
      await pauseSchedulerJob(jobId);
      setSuccessMessage(`Job 已暫停：${jobId}`);
      await refreshSchedulerData();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : `Pause job 失敗：${jobId}`;
      setActionError(message);
    } finally {
      setActionLoadingKey(null);
    }
  };

  const handleResumeJob = async (jobId: string) => {
    setActionError(null);
    setSuccessMessage(null);
    setActionLoadingKey(`${jobId}:resume`);

    try {
      await resumeSchedulerJob(jobId);
      setSuccessMessage(`Job 已恢復：${jobId}`);
      await refreshSchedulerData();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : `Resume job 失敗：${jobId}`;
      setActionError(message);
    } finally {
      setActionLoadingKey(null);
    }
  };

  const handleRunNowJob = async (jobId: string) => {
    setActionError(null);
    setSuccessMessage(null);
    setActionLoadingKey(`${jobId}:run-now`);

    try {
      const result = await runSchedulerJobNow(jobId);
      const resultText = JSON.stringify(result.result);
      setSuccessMessage(`Run Now 成功：${jobId} / result=${resultText}`);
      await refreshSchedulerData();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : `Run Now 失敗：${jobId}`;
      setActionError(message);
    } finally {
      setActionLoadingKey(null);
    }
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
            Scheduler
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
            查看排程狀態、jobs 清單，並執行 pause / resume / run-now
          </p>
        </div>

        {pageError && <div style={errorBannerStyle}>{pageError}</div>}

        {actionError && <div style={errorBannerStyle}>{actionError}</div>}

        {successMessage && <div style={successBannerStyle}>{successMessage}</div>}

        <div style={{ marginBottom: "20px" }}>
          <SchedulerStatusCards statusInfo={statusInfo} loading={loadingStatus} />
        </div>

        <div
          style={{
            marginBottom: "20px",
            padding: "20px",
            borderRadius: "20px",
            backgroundColor: "#fff",
            border: "1px solid #e2e8f0",
            boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
            display: "flex",
            gap: "12px",
            flexWrap: "wrap",
          }}
        >
          <button
            onClick={handlePauseScheduler}
            disabled={schedulerActionLoading !== null}
            style={secondaryButtonStyle}
          >
            {schedulerActionLoading === "pause" ? "Pause 中..." : "Pause Scheduler"}
          </button>

          <button
            onClick={handleResumeScheduler}
            disabled={schedulerActionLoading !== null}
            style={primaryButtonStyle}
          >
            {schedulerActionLoading === "resume" ? "Resume 中..." : "Resume Scheduler"}
          </button>
        </div>

        <SchedulerJobsList
          jobs={jobs}
          loading={loadingJobs}
          error={pageError}
          hasLoaded={hasLoaded}
          actionLoadingKey={actionLoadingKey}
          onPauseJob={handlePauseJob}
          onResumeJob={handleResumeJob}
          onRunNowJob={handleRunNowJob}
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

const errorBannerStyle: React.CSSProperties = {
  marginBottom: "16px",
  border: "1px solid #fecaca",
  backgroundColor: "#fef2f2",
  color: "#b91c1c",
  borderRadius: "18px",
  padding: "16px 20px",
};

const successBannerStyle: React.CSSProperties = {
  marginBottom: "16px",
  border: "1px solid #a7f3d0",
  backgroundColor: "#ecfdf5",
  color: "#047857",
  borderRadius: "18px",
  padding: "16px 20px",
};