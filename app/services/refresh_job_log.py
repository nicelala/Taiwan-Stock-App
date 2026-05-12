from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RefreshJobLogItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_name: str
    market: str
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    duration_ms: int | None = None
    inserted_or_updated_count: int | None = None
    skipped_count: int | None = None
    error_message: str | None = None
    trigger_source: str


class RefreshJobLogListResponse(BaseModel):
    items: list[RefreshJobLogItemResponse]
    count: int