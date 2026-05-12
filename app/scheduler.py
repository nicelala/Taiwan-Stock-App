from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.stock_service import StockService
from app.services.dividend_service import DividendService

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def run_refresh_stocks_job(market: str, trigger_source: str = "scheduler") -> dict:
    """
    由 scheduler 或 API 手動觸發的 stock refresh job。
    """
    db = SessionLocal()
    try:
        service = StockService(db)
        return service.sync_from_source(market, trigger_source=trigger_source)
    except Exception:
        logger.exception(
            "Scheduler stock refresh failed: market=%s trigger_source=%s",
            market,
            trigger_source,
        )
        raise
    finally:
        db.close()


def run_refresh_dividends_job(market: str, trigger_source: str = "scheduler") -> dict:
    """
    由 scheduler 或 API 手動觸發的 dividend refresh job。
    先確保股票基本資料存在，再刷股利。
    """
    db = SessionLocal()
    try:
        stock_service = StockService(db)
        stock_service.sync_from_source(market, trigger_source=trigger_source)

        dividend_service = DividendService(db)
        return dividend_service.sync_from_source(market, trigger_source=trigger_source)
    except Exception:
        logger.exception(
            "Scheduler dividend refresh failed: market=%s trigger_source=%s",
            market,
            trigger_source,
        )
        raise
    finally:
        db.close()


def build_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="Asia/Taipei")

    # 每日 stock refresh
    scheduler.add_job(
        run_refresh_stocks_job,
        trigger=CronTrigger(
            hour=settings.scheduler_stocks_hour,
            minute=settings.scheduler_stocks_minute,
        ),
        args=["TWSE"],
        id="refresh_stocks_twse",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )

    scheduler.add_job(
        run_refresh_stocks_job,
        trigger=CronTrigger(
            hour=settings.scheduler_stocks_hour,
            minute=settings.scheduler_stocks_minute,
        ),
        args=["TPEX"],
        id="refresh_stocks_tpex",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )

    # 每日 dividend refresh
    scheduler.add_job(
        run_refresh_dividends_job,
        trigger=CronTrigger(
            hour=settings.scheduler_dividends_hour,
            minute=settings.scheduler_dividends_minute,
        ),
        args=["TWSE"],
        id="refresh_dividends_twse",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )

    scheduler.add_job(
        run_refresh_dividends_job,
        trigger=CronTrigger(
            hour=settings.scheduler_dividends_hour,
            minute=settings.scheduler_dividends_minute,
        ),
        args=["TPEX"],
        id="refresh_dividends_tpex",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )

    return scheduler


def start_scheduler() -> BackgroundScheduler | None:
    """
    啟動 scheduler。
    若 ENABLE_SCHEDULER=false，則不啟動。
    """
    global _scheduler

    if not settings.enable_scheduler:
        logger.info("Scheduler disabled by settings.enable_scheduler=False")
        return None

    if _scheduler is not None and _scheduler.running:
        logger.info("Scheduler already running")
        return _scheduler

    scheduler = build_scheduler()
    scheduler.start()
    _scheduler = scheduler

    logger.info("Scheduler started with 4 jobs")
    return scheduler


def shutdown_scheduler(scheduler: BackgroundScheduler | None) -> None:
    """
    關閉 scheduler。
    """
    if scheduler is None:
        return

    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shutdown completed")