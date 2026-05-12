export type RefreshJobName = "refresh_stocks" | "refresh_dividends";
export type RefreshMarket = "TWSE" | "TPEX";
export type RefreshStatus = "running" | "success" | "failed";
export type TriggerSource = "api" | "scheduler" | "api_manual" | string;

export type RefreshLogItem = {
  id: number;
  job_name: RefreshJobName;
  market: RefreshMarket;
  status: RefreshStatus;
  started_at: string;
  finished_at?: string | null;
  duration_ms?: number | null;
  inserted_or_updated_count?: number | null;
  skipped_count?: number | null;
  error_message?: string | null;
  trigger_source: TriggerSource;
};

export type RefreshLogsResponse = {
  items: RefreshLogItem[];
  count: number;
};

export type RefreshLogsParams = {
  job_name?: RefreshJobName;
  market?: RefreshMarket;
  status?: RefreshStatus;
  limit?: number;
  offset?: number;
};
