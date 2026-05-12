export type SchedulerStatusResponse = {
    enabled: boolean;
    running: boolean;
    job_count: number;
    jobs: string[];
  };
  
  export type SchedulerJobItem = {
    id: string;
    name: string;
    next_run_time?: string | null;
    trigger: string;
    args: string[];
    paused: boolean;
  };
  
  export type SchedulerJobsResponse = {
    items: SchedulerJobItem[];
    count: number;
  };
  
  export type SchedulerControlResponse = {
    status: string;
    scheduler_running?: boolean | null;
    job_id?: string | null;
    paused?: boolean | null;
  };
  
  export type SchedulerRunNowResponse = {
    status: string;
    job_id: string;
    result: Record<string, unknown>;
  };