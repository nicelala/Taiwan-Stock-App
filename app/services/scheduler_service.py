from __future__ import annotations

from typing import Any

from apscheduler.schedulers.base import STATE_RUNNING

from app.core.config import settings
from app.scheduler import run_refresh_stocks_job, run_refresh_dividends_job


class SchedulerService:
    VALID_JOB_IDS = {
        "refresh_stocks_twse",
        "refresh_stocks_tpex",
        "refresh_dividends_twse",
        "refresh_dividends_tpex",
    }

    def get_status(self, scheduler: Any) -> dict:
        if scheduler is None:
            return {
                "enabled": settings.enable_scheduler,
                "running": False,
                "job_count": 0,
                "jobs": [],
            }

        jobs = scheduler.get_jobs()
        running = self._is_running(scheduler)

        return {
            "enabled": settings.enable_scheduler,
            "running": running,
            "job_count": len(jobs),
            "jobs": [str(job.id) for job in jobs],
        }

    def list_jobs(self, scheduler: Any) -> list[dict]:
        if scheduler is None:
            return []

        jobs = scheduler.get_jobs()
        items: list[dict] = []

        for job in jobs:
            args = getattr(job, "args", ()) or ()
            next_run_time = getattr(job, "next_run_time", None)

            items.append(
                {
                    "id": str(job.id),
                    "name": str(getattr(job, "name", "")),
                    "next_run_time": next_run_time,
                    "trigger": str(getattr(job, "trigger", "")),
                    "args": [str(arg) for arg in args],
                    "paused": next_run_time is None,
                }
            )

        return items

    def pause_scheduler(self, scheduler: Any) -> dict:
        self._ensure_enabled()
        self._ensure_scheduler_exists(scheduler)

        # 冪等：已 paused 也回 success
        if self._is_running(scheduler):
            scheduler.pause()

        return {
            "status": "success",
            "scheduler_running": self._is_running(scheduler),
        }

    def resume_scheduler(self, scheduler: Any) -> dict:
        self._ensure_enabled()
        self._ensure_scheduler_exists(scheduler)

        # 冪等：已 running 也回 success
        if not self._is_running(scheduler):
            scheduler.resume()

        return {
            "status": "success",
            "scheduler_running": self._is_running(scheduler),
        }

    def pause_job(self, scheduler: Any, job_id: str) -> dict:
        self._ensure_enabled()
        self._ensure_scheduler_exists(scheduler)

        job = self._get_job_or_raise(scheduler, job_id)

        # 冪等：已 paused 也回 success
        if getattr(job, "next_run_time", None) is not None:
            scheduler.pause_job(job_id)
            job = self._get_job_or_raise(scheduler, job_id)

        return {
            "status": "success",
            "job_id": job_id,
            "paused": getattr(job, "next_run_time", None) is None,
        }

    def resume_job(self, scheduler: Any, job_id: str) -> dict:
        self._ensure_enabled()
        self._ensure_scheduler_exists(scheduler)

        self._get_job_or_raise(scheduler, job_id)

        scheduler.resume_job(job_id)
        job = self._get_job_or_raise(scheduler, job_id)

        return {
            "status": "success",
            "job_id": job_id,
            "paused": getattr(job, "next_run_time", None) is None,
        }

    def run_job_now(self, scheduler: Any, job_id: str) -> dict:
        self._ensure_enabled()
        self._ensure_scheduler_exists(scheduler)

        # 即使整體 scheduler 被 pause，仍允許手動 run-now
        self._get_job_or_raise(scheduler, job_id)

        if job_id == "refresh_stocks_twse":
            result = run_refresh_stocks_job("TWSE", trigger_source="api_manual")
        elif job_id == "refresh_stocks_tpex":
            result = run_refresh_stocks_job("TPEX", trigger_source="api_manual")
        elif job_id == "refresh_dividends_twse":
            result = run_refresh_dividends_job("TWSE", trigger_source="api_manual")
        elif job_id == "refresh_dividends_tpex":
            result = run_refresh_dividends_job("TPEX", trigger_source="api_manual")
        else:
            raise ValueError("SCHEDULER_JOB_NOT_FOUND")

        return {
            "status": "success",
            "job_id": job_id,
            "result": result,
        }

    # --------------------------------------------------
    # internal helpers
    # --------------------------------------------------

    def _ensure_enabled(self) -> None:
        if not settings.enable_scheduler:
            raise ValueError("SCHEDULER_DISABLED")

    def _ensure_scheduler_exists(self, scheduler: Any) -> None:
        if scheduler is None:
            raise ValueError("SCHEDULER_NOT_RUNNING")

    def _get_job_or_raise(self, scheduler: Any, job_id: str):
        if job_id not in self.VALID_JOB_IDS:
            raise ValueError("SCHEDULER_JOB_NOT_FOUND")

        job = None
        if hasattr(scheduler, "get_job"):
            job = scheduler.get_job(job_id)

        if job is None and hasattr(scheduler, "get_jobs"):
            for item in scheduler.get_jobs():
                if str(getattr(item, "id", "")) == job_id:
                    job = item
                    break

        if job is None:
            raise ValueError("SCHEDULER_JOB_NOT_FOUND")

        return job

    def _is_running(self, scheduler: Any) -> bool:
        if scheduler is None:
            return False

        state = getattr(scheduler, "state", None)
        if state is not None:
            return state == STATE_RUNNING

        paused = getattr(scheduler, "paused", None)
        if paused is not None:
            return not bool(paused)

        return bool(getattr(scheduler, "running", False))