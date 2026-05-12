from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.utils import now_utc
from app.models.refresh_job_log import RefreshJobLog


class RefreshJobLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_running(
        self,
        job_name: str,
        market: str,
        trigger_source: str = "api",
    ) -> RefreshJobLog:
        obj = RefreshJobLog(
            job_name=job_name,
            market=market,
            status="running",
            started_at=now_utc(),
            trigger_source=trigger_source,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def mark_success(
        self,
        log_id: int,
        inserted_or_updated_count: int,
        skipped_count: int = 0,
    ) -> RefreshJobLog | None:
        obj = self.db.query(RefreshJobLog).filter(RefreshJobLog.id == log_id).first()
        if obj is None:
            return None

        finished_at = now_utc()
        obj.status = "success"
        obj.finished_at = finished_at
        obj.duration_ms = self._duration_ms(obj.started_at, finished_at)
        obj.inserted_or_updated_count = inserted_or_updated_count
        obj.skipped_count = skipped_count
        obj.error_message = None

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def mark_failed(
        self,
        log_id: int,
        error_message: str,
    ) -> RefreshJobLog | None:
        obj = self.db.query(RefreshJobLog).filter(RefreshJobLog.id == log_id).first()
        if obj is None:
            return None

        finished_at = now_utc()
        obj.status = "failed"
        obj.finished_at = finished_at
        obj.duration_ms = self._duration_ms(obj.started_at, finished_at)
        obj.error_message = error_message[:5000] if error_message else None

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list_logs(
        self,
        job_name: str | None = None,
        market: str | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[RefreshJobLog]:
        query = self.db.query(RefreshJobLog)

        if job_name is not None:
            query = query.filter(RefreshJobLog.job_name == job_name)

        if market is not None:
            query = query.filter(RefreshJobLog.market == market)

        if status is not None:
            query = query.filter(RefreshJobLog.status == status)

        return (
            query.order_by(
                RefreshJobLog.started_at.desc(),
                RefreshJobLog.id.desc(),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

    def _duration_ms(self, started_at, finished_at) -> int | None:
        if started_at is None or finished_at is None:
            return None
        delta = finished_at - started_at
        return int(delta.total_seconds() * 1000)