import type {
    SchedulerControlResponse,
    SchedulerJobsResponse,
    SchedulerRunNowResponse,
    SchedulerStatusResponse,
  } from "../types/scheduler";
  
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
  
  type ApiErrorDetail =
    | {
        code?: string;
        message?: string;
      }
    | string
    | null;
  
  type ApiErrorResponse = {
    detail?: ApiErrorDetail;
  };
  
  function parseApiError(payload: ApiErrorResponse | null): string {
    if (!payload?.detail) return "操作失敗，請稍後再試。";
  
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
  
    if (payload.detail.message) {
      return payload.detail.message;
    }
  
    if (payload.detail.code) {
      return payload.detail.code;
    }
  
    return "操作失敗，請稍後再試。";
  }
  
  async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
        ...(options?.headers ?? {}),
      },
      ...options,
    });
  
    if (!response.ok) {
      let errorPayload: ApiErrorResponse | null = null;
  
      try {
        errorPayload = await response.json();
      } catch {
        errorPayload = null;
      }
  
      throw new Error(parseApiError(errorPayload));
    }
  
    return (await response.json()) as T;
  }
  
  export async function getSchedulerStatus(): Promise<SchedulerStatusResponse> {
    return await requestJson<SchedulerStatusResponse>(
      `${API_BASE_URL}/api/v1/admin/scheduler/status`
    );
  }
  
  export async function getSchedulerJobs(): Promise<SchedulerJobsResponse> {
    return await requestJson<SchedulerJobsResponse>(
      `${API_BASE_URL}/api/v1/admin/scheduler/jobs`
    );
  }
  
  export async function pauseScheduler(): Promise<SchedulerControlResponse> {
    return await requestJson<SchedulerControlResponse>(
      `${API_BASE_URL}/api/v1/admin/scheduler/pause`,
      {
        method: "POST",
      }
    );
  }
  
  export async function resumeScheduler(): Promise<SchedulerControlResponse> {
    return await requestJson<SchedulerControlResponse>(
      `${API_BASE_URL}/api/v1/admin/scheduler/resume`,
      {
        method: "POST",
      }
    );
  }
  
  export async function pauseSchedulerJob(jobId: string): Promise<SchedulerControlResponse> {
    return await requestJson<SchedulerControlResponse>(
      `${API_BASE_URL}/api/v1/admin/scheduler/jobs/${jobId}/pause`,
      {
        method: "POST",
      }
    );
  }
  
  export async function resumeSchedulerJob(jobId: string): Promise<SchedulerControlResponse> {
    return await requestJson<SchedulerControlResponse>(
      `${API_BASE_URL}/api/v1/admin/scheduler/jobs/${jobId}/resume`,
      {
        method: "POST",
      }
    );
  }
  
  export async function runSchedulerJobNow(jobId: string): Promise<SchedulerRunNowResponse> {
    return await requestJson<SchedulerRunNowResponse>(
      `${API_BASE_URL}/api/v1/admin/scheduler/jobs/${jobId}/run-now`,
      {
        method: "POST",
      }
    );
  }