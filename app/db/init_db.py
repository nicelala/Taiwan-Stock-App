from __future__ import annotations

from app.db.base import Base
from app.db.session import engine

# 確保 metadata 收集到所有 models
from app.models.stock_basic import StockBasic  # noqa: F401
from app.models.dividend_history import DividendHistory  # noqa: F401
from app.models.refresh_job_log import RefreshJobLog  # noqa: F401


def init_db():
    Base.metadata.create_all(bind=engine)