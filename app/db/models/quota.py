from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, ForeignKey

from app.db.base import BaseModel


class QuotaModel(BaseModel):
    __tablename__ = "quotas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_code: Mapped[str] = mapped_column(String(50))
    key: Mapped[str] = mapped_column(String(100))
    limit: Mapped[int] = mapped_column()


class UsageModel(BaseModel):
    __tablename__ = "usage"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(100))
    value: Mapped[int] = mapped_column(default=0)
    period_start: Mapped[datetime] = mapped_column(DateTime)
    period_end: Mapped[datetime] = mapped_column(DateTime)
