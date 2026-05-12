from app.models.refresh_job_log import RefreshJobLog


def test_list_refresh_logs_success(client, db_session):
    db_session.add_all(
        [
            RefreshJobLog(
                job_name="refresh_stocks",
                market="TWSE",
                status="success",
                trigger_source="api",
            ),
            RefreshJobLog(
                job_name="refresh_dividends",
                market="TPEX",
                status="failed",
                trigger_source="api",
                error_message="boom",
            ),
        ]
    )
    db_session.commit()

    resp = client.get("/api/v1/admin/refresh/logs")
    assert resp.status_code == 200

    data = resp.json()
    assert "items" in data
    assert "count" in data
    assert data["count"] == len(data["items"])
    assert data["count"] == 2


def test_list_refresh_logs_filter_by_market(client, db_session):
    db_session.add_all(
        [
            RefreshJobLog(
                job_name="refresh_stocks",
                market="TWSE",
                status="success",
                trigger_source="api",
            ),
            RefreshJobLog(
                job_name="refresh_dividends",
                market="TPEX",
                status="success",
                trigger_source="api",
            ),
        ]
    )
    db_session.commit()

    resp = client.get("/api/v1/admin/refresh/logs?market=TPEX")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["items"][0]["market"] == "TPEX"


def test_list_refresh_logs_filter_by_status(client, db_session):
    db_session.add_all(
        [
            RefreshJobLog(
                job_name="refresh_stocks",
                market="TWSE",
                status="success",
                trigger_source="api",
            ),
            RefreshJobLog(
                job_name="refresh_dividends",
                market="TPEX",
                status="failed",
                trigger_source="api",
                error_message="boom",
            ),
        ]
    )
    db_session.commit()

    resp = client.get("/api/v1/admin/refresh/logs?status=failed")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["items"][0]["status"] == "failed"


def test_list_refresh_logs_filter_by_job_name(client, db_session):
    db_session.add_all(
        [
            RefreshJobLog(
                job_name="refresh_stocks",
                market="TWSE",
                status="success",
                trigger_source="api",
            ),
            RefreshJobLog(
                job_name="refresh_dividends",
                market="TPEX",
                status="success",
                trigger_source="api",
            ),
        ]
    )
    db_session.commit()

    resp = client.get("/api/v1/admin/refresh/logs?job_name=refresh_dividends")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert data["items"][0]["job_name"] == "refresh_dividends"


def test_list_refresh_logs_limit_and_offset(client, db_session):
    db_session.add_all(
        [
            RefreshJobLog(
                job_name="refresh_stocks",
                market="TWSE",
                status="success",
                trigger_source="api",
            ),
            RefreshJobLog(
                job_name="refresh_dividends",
                market="TWSE",
                status="success",
                trigger_source="api",
            ),
            RefreshJobLog(
                job_name="refresh_dividends",
                market="TPEX",
                status="failed",
                trigger_source="api",
                error_message="boom",
            ),
        ]
    )
    db_session.commit()

    resp = client.get("/api/v1/admin/refresh/logs?limit=1&offset=1")
    assert resp.status_code == 200

    data = resp.json()
    assert data["count"] == 1
    assert len(data["items"]) == 1


def test_list_refresh_logs_invalid_market_returns_422(client):
    resp = client.get("/api/v1/admin/refresh/logs?market=BAD")
    assert resp.status_code == 422

    data = resp.json()
    assert data["detail"]["code"] == "INVALID_MARKET"


def test_list_refresh_logs_invalid_status_returns_422(client):
    resp = client.get("/api/v1/admin/refresh/logs?status=BAD")
    assert resp.status_code == 422

    data = resp.json()
    assert data["detail"]["code"] == "INVALID_STATUS"


def test_list_refresh_logs_invalid_job_name_returns_422(client):
    resp = client.get("/api/v1/admin/refresh/logs?job_name=BAD")
    assert resp.status_code == 422

    data = resp.json()
    assert data["detail"]["code"] == "INVALID_JOB_NAME"


def test_list_refresh_logs_limit_is_clamped_to_100(client, db_session):
    for _ in range(3):
        db_session.add(
            RefreshJobLog(
                job_name="refresh_stocks",
                market="TWSE",
                status="success",
                trigger_source="api",
            )
        )
    db_session.commit()

    resp = client.get("/api/v1/admin/refresh/logs?limit=9999")
    assert resp.status_code == 200

    data = resp.json()
    # 因為資料本來只有 3 筆，clamp 後也只會回 3 筆
    assert data["count"] == 3