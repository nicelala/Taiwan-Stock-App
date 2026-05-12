from __future__ import annotations

from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.core.utils import now_utc


class RefreshJobLog(Base):
    __tablename__ = "refresh_job_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    job_name: Mapped[str] = mapped_column(String(64), nullable=False)
    market: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)

    started_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=now_utc)
    finished_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    inserted_or_updated_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    skipped_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    trigger_source: Mapped[str] = mapped_column(String(32), nullable=False, default="api")