from __future__ import annotations
from datetime import datetime

from pydantic import BaseModel


class SchedulerStatusResponse(BaseModel):
    enabled: bool
    running: bool
    job_count: int
    jobs: list[str]


class SchedulerJobItemResponse(BaseModel):
    id: str
    name: str
    next_run_time: datetime | None = None
    trigger: str
    args: list[str]
    paused: bool


class SchedulerJobsListResponse(BaseModel):
    items: list[SchedulerJobItemResponse]
    count: int


class SchedulerControlResponse(BaseModel):
    status: str
    scheduler_running: bool | None = None
    job_id: str | None = None
    paused: bool | None = None


class SchedulerRunNowResponse(BaseModel):
    status: str
    job_id: str
    result: dict

