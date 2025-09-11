from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, ForeignKey

from app.db.base import Base


class Quota(Base):
    __tablename__ = "quotas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)           # ID записи
    plan_code: Mapped[str] = mapped_column(String(50))                              # тариф: free/pro
    key: Mapped[str] = mapped_column(String(100))                                   # напр. "workouts.count"
    limit: Mapped[int] = mapped_column()                                            # лимит по тарифу


class Usage(Base):
    __tablename__ = "usage"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)           # ID строки
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))# чей usage
    key: Mapped[str] = mapped_column(String(100))                                   # напр. "share.users.monthly"
    value: Mapped[int] = mapped_column(default=0)                                   # сколько использовано
    period_start: Mapped[datetime] = mapped_column(DateTime)                        # начало периода
    period_end: Mapped[datetime] = mapped_column(DateTime)                          # конец периода
