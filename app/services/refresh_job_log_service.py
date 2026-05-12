from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.refresh_job_log_repository import RefreshJobLogRepository


class RefreshJobLogService:
    VALID_JOB_NAMES = {"refresh_stocks", "refresh_dividends"}
    VALID_MARKETS = {"TWSE", "TPEX"}
    VALID_STATUS = {"running", "success", "failed"}

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = RefreshJobLogRepository(db)

    def list_logs(
        self,
        job_name: str | None = None,
        market: str | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ):
        normalized_job_name = self._normalize_job_name(job_name)
        normalized_market = self._normalize_market(market)
        normalized_status = self._normalize_status(status)

        normalized_limit = self._normalize_limit(limit)
        normalized_offset = self._normalize_offset(offset)

        return self.repo.list_logs(
            job_name=normalized_job_name,
            market=normalized_market,
            status=normalized_status,
            limit=normalized_limit,
            offset=normalized_offset,
        )

    def _normalize_job_name(self, job_name: str | None) -> str | None:
        if job_name is None:
            return None

        text = str(job_name).strip().lower()
        if text not in self.VALID_JOB_NAMES:
            raise ValueError("INVALID_JOB_NAME")
        return text

    def _normalize_market(self, market: str | None) -> str | None:
        if market is None:
            return None

        text = str(market).strip().upper()
        if text not in self.VALID_MARKETS:
            raise ValueError("INVALID_MARKET")
        return text

    def _normalize_status(self, status: str | None) -> str | None:
        if status is None:
            return None

        text = str(status).strip().lower()
        if text not in self.VALID_STATUS:
            raise ValueError("INVALID_STATUS")
        return text

    def _normalize_limit(self, limit: int | None) -> int:
        if limit is None:
            return 20

        try:
            value = int(limit)
        except Exception:
            return 20

        if value < 1:
            return 1

        if value > 100:
            return 100

        return value

    def _normalize_offset(self, offset: int | None) -> int:
        if offset is None:
            return 0

        try:
            value = int(offset)
        except Exception:
            return 0

        if value < 0:
            return 0

        return value