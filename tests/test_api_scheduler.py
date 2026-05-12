from datetime import datetime
from types import SimpleNamespace

from apscheduler.schedulers.base import STATE_RUNNING, STATE_PAUSED

from app.core.config import settings
from app.models.refresh_job_log import RefreshJobLog
from app.services.stock_service import StockService
from app.services.dividend_service import DividendService


class FakeJob:
    def __init__(self, job_id, name, next_run_time, trigger, args):
        self.id = job_id
        self.name = name
        self.next_run_time = next_run_time
        self._saved_next_run_time = next_run_time
        self.trigger = trigger
        self.args = args


class FakeScheduler:
    def __init__(self, running=True, jobs=None):
        self._jobs = {job.id: job for job in (jobs or [])}
        self.state = STATE_RUNNING if running else STATE_PAUSED

    @property
    def running(self):
        return self.state == STATE_RUNNING

    def get_jobs(self):
        return list(self._jobs.values())

    def get_job(self, job_id):
        return self._jobs.get(job_id)

    def pause(self):
        self.state = STATE_PAUSED

    def resume(self):
        self.state = STATE_RUNNING

    def pause_job(self, job_id):
        job = self.get_job(job_id)
        if job is not None:
            job.next_run_time = None

    def resume_job(self, job_id):
        job = self.get_job(job_id)
        if job is not None:
            job.next_run_time = job._saved_next_run_time

    def shutdown(self, wait=False):
        self.state = STATE_PAUSED


def test_get_scheduler_status_when_disabled_returns_not_running(client):
    from app.main import app

    app.state.scheduler = None
    settings.enable_scheduler = False

    resp = client.get("/api/v1/admin/scheduler/status")
    assert resp.status_code == 200

    data = resp.json()
    assert data["enabled"] is False
    assert data["running"] is False
    assert data["job_count"] == 0
    assert data["jobs"] == []


def test_get_scheduler_status_when_running_returns_jobs(client):
    from app.main import app

    settings.enable_scheduler = True

    fake_scheduler = FakeScheduler(
        running=True,
        jobs=[
            FakeJob(
                "refresh_stocks_twse",
                "run_refresh_stocks_job",
                datetime(2026, 5, 1, 6, 0, 0),
                "cron[hour='6', minute='0']",
                ["TWSE"],
            ),
            FakeJob(
                "refresh_dividends_tpex",
                "run_refresh_dividends_job",
                datetime(2026, 5, 1, 6, 10, 0),
                "cron[hour='6', minute='10']",
                ["TPEX"],
            ),
        ],
    )
    app.state.scheduler = fake_scheduler

    resp = client.get("/api/v1/admin/scheduler/status")
    assert resp.status_code == 200

    data = resp.json()
    assert data["enabled"] is True
    assert data["running"] is True
    assert data["job_count"] == 2
    assert "refresh_stocks_twse" in data["jobs"]
    assert "refresh_dividends_tpex" in data["jobs"]


def test_get_scheduler_jobs_returns_items(client):
    from app.main import app

    settings.enable_scheduler = True

    fake_scheduler = FakeScheduler(
        running=True,
        jobs=[
            FakeJob(
                "refresh_stocks_twse",
                "run_refresh_stocks_job",
                datetime(2026, 5, 1, 6, 0, 0),
                "cron[hour='6', minute='0']",
                ["TWSE"],
            ),
            FakeJob(
                "refresh_dividends_tpex",
                "run_refresh_dividends_job",
                datetime(2026, 5, 1, 6, 10, 0),
                "cron[hour='6', minute='10']",
                ["TPEX"],
            ),
        ],
    )
    app.state.scheduler = fake_scheduler

    resp = client.get("/api/v1/admin/scheduler/jobs")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 2
    assert len(data["items"]) == 2

    first = data["items"][0]
    assert "id" in first
    assert "name" in first
    assert "next_run_time" in first
    assert "trigger" in first
    assert "args" in first
    assert "paused" in first


def test_get_scheduler_jobs_when_disabled_returns_empty_list(client):
    from app.main import app

    app.state.scheduler = None
    settings.enable_scheduler = False

    resp = client.get("/api/v1/admin/scheduler/jobs")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 0
    assert data["items"] == []


def test_pause_scheduler_success(client):
    from app.main import app

    settings.enable_scheduler = True
    app.state.scheduler = FakeScheduler(running=True, jobs=[])

    resp = client.post("/api/v1/admin/scheduler/pause")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "success"
    assert data["scheduler_running"] is False


def test_resume_scheduler_success(client):
    from app.main import app

    settings.enable_scheduler = True
    app.state.scheduler = FakeScheduler(running=False, jobs=[])

    resp = client.post("/api/v1/admin/scheduler/resume")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "success"
    assert data["scheduler_running"] is True


def test_pause_scheduler_when_disabled_returns_409(client):
    from app.main import app

    settings.enable_scheduler = False
    app.state.scheduler = None

    resp = client.post("/api/v1/admin/scheduler/pause")
    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "SCHEDULER_DISABLED"


def test_pause_scheduler_when_not_running_returns_503(client):
    from app.main import app

    settings.enable_scheduler = True
    app.state.scheduler = None

    resp = client.post("/api/v1/admin/scheduler/pause")
    assert resp.status_code == 503
    assert resp.json()["detail"]["code"] == "SCHEDULER_NOT_RUNNING"


def test_pause_scheduler_job_success(client):
    from app.main import app

    settings.enable_scheduler = True
    fake_scheduler = FakeScheduler(
        running=True,
        jobs=[
            FakeJob(
                "refresh_stocks_twse",
                "run_refresh_stocks_job",
                datetime(2026, 5, 1, 6, 0, 0),
                "cron[hour='6', minute='0']",
                ["TWSE"],
            )
        ],
    )
    app.state.scheduler = fake_scheduler

    resp = client.post("/api/v1/admin/scheduler/jobs/refresh_stocks_twse/pause")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "success"
    assert data["job_id"] == "refresh_stocks_twse"
    assert data["paused"] is True

    resp2 = client.get("/api/v1/admin/scheduler/jobs")
    assert resp2.status_code == 200
    assert resp2.json()["items"][0]["paused"] is True


def test_resume_scheduler_job_success(client):
    from app.main import app

    settings.enable_scheduler = True
    job = FakeJob(
        "refresh_stocks_twse",
        "run_refresh_stocks_job",
        datetime(2026, 5, 1, 6, 0, 0),
        "cron[hour='6', minute='0']",
        ["TWSE"],
    )
    job.next_run_time = None

    fake_scheduler = FakeScheduler(running=True, jobs=[job])
    app.state.scheduler = fake_scheduler

    resp = client.post("/api/v1/admin/scheduler/jobs/refresh_stocks_twse/resume")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "success"
    assert data["job_id"] == "refresh_stocks_twse"
    assert data["paused"] is False


def test_scheduler_job_not_found_returns_404(client):
    from app.main import app

    settings.enable_scheduler = True
    app.state.scheduler = FakeScheduler(running=True, jobs=[])

    resp = client.post("/api/v1/admin/scheduler/jobs/not_exist/pause")
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "SCHEDULER_JOB_NOT_FOUND"


def test_run_scheduler_job_now_for_stocks_writes_api_manual_log(client, db_session, monkeypatch):
    from app.main import app

    settings.enable_scheduler = True
    app.state.scheduler = FakeScheduler(
        running=True,
        jobs=[
            FakeJob(
                "refresh_stocks_twse",
                "run_refresh_stocks_job",
                datetime(2026, 5, 1, 6, 0, 0),
                "cron[hour='6', minute='0']",
                ["TWSE"],
            )
        ],
    )

    def fake_fetch_stock_rows(self, market):
        return [
            {
                "公司代號": "1101",
                "公司名稱": "台灣水泥股份有限公司",
                "公司簡稱": "台泥",
                "產業別": "01",
                "普通股每股面額": "10",
                "上市日期": "1962/02/09",
                "實收資本額": "77500000000",
                "已發行普通股數或TDR原股發行股數": "7750000000",
            }
        ]

    monkeypatch.setattr(StockService, "_fetch_stock_rows", fake_fetch_stock_rows)

    resp = client.post("/api/v1/admin/scheduler/jobs/refresh_stocks_twse/run-now")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "success"
    assert data["job_id"] == "refresh_stocks_twse"
    assert data["result"]["market"] == "TWSE"
    assert data["result"]["count"] == 1

    db_session.expire_all()
    log = db_session.query(RefreshJobLog).order_by(RefreshJobLog.id.desc()).first()
    assert log is not None
    assert log.job_name == "refresh_stocks"
    assert log.market == "TWSE"
    assert log.trigger_source == "api_manual"


def test_run_scheduler_job_now_for_dividends_success(client, db_session, monkeypatch):
    from app.main import app

    settings.enable_scheduler = True
    app.state.scheduler = FakeScheduler(
        running=True,
        jobs=[
            FakeJob(
                "refresh_dividends_tpex",
                "run_refresh_dividends_job",
                datetime(2026, 5, 1, 6, 10, 0),
                "cron[hour='6', minute='10']",
                ["TPEX"],
            )
        ],
    )

    def fake_fetch_stock_rows(self, market):
        return [
            {
                "公司代號": "6488",
                "公司名稱": "環球晶圓股份有限公司",
                "公司簡稱": "環球晶",
                "產業別": "24",
                "普通股每股面額": "10",
                "上櫃日期": "2015/09/25",
                "實收資本額": "4781137250",
                "已發行普通股數或TDR原股發行股數": "478113725",
            }
        ]

    def fake_fetch_dividend_rows(self, market):
        return [
            {
                "公司代號": "6488",
                "股利年度": "114",
                "期別": "1",
                "決議進度": "董事會決議",
                "董事會決議日": "2026/03/03",
                "現金股利(元/股)": "5.7",
                "股票股利(元/股)": "0.0",
            }
        ]

    monkeypatch.setattr(StockService, "_fetch_stock_rows", fake_fetch_stock_rows)
    monkeypatch.setattr(DividendService, "_fetch_dividend_rows", fake_fetch_dividend_rows)

    resp = client.post("/api/v1/admin/scheduler/jobs/refresh_dividends_tpex/run-now")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "success"
    assert data["job_id"] == "refresh_dividends_tpex"
    assert data["result"]["market"] == "TPEX"
    assert "count" in data["result"]


def test_run_scheduler_job_now_when_disabled_returns_409(client):
    from app.main import app

    settings.enable_scheduler = False
    app.state.scheduler = None

    resp = client.post("/api/v1/admin/scheduler/jobs/refresh_stocks_twse/run-now")
    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "SCHEDULER_DISABLED"


def test_run_scheduler_job_now_when_scheduler_not_running_returns_503(client):
    from app.main import app

    settings.enable_scheduler = True
    app.state.scheduler = None

    resp = client.post("/api/v1/admin/scheduler/jobs/refresh_stocks_twse/run-now")
    assert resp.status_code == 503
    assert resp.json()["detail"]["code"] == "SCHEDULER_NOT_RUNNING"


def test_run_scheduler_job_now_job_not_found_returns_404(client):
    from app.main import app

    settings.enable_scheduler = True
    app.state.scheduler = FakeScheduler(running=True, jobs=[])

    resp = client.post("/api/v1/admin/scheduler/jobs/not_exist/run-now")
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "SCHEDULER_JOB_NOT_FOUND"