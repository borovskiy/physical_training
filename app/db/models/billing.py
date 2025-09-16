from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, ForeignKey

from app.db.base import BaseModel


class BillingTransactionModel(BaseModel):
    __tablename__ = "billing_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)               # ID транзакции
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))    # чей платёж
    provider: Mapped[str] = mapped_column(String(50), default="stripe")                 # провайдер (stripe и т.д.)
    external_id: Mapped[str] = mapped_column(String(255))                               # ID у провайдера
    amount_cents: Mapped[int] = mapped_column()                                         # сумма (в центах)
    currency: Mapped[str] = mapped_column(String(10), default="USD")                    # валюта
    status: Mapped[str] = mapped_column(String(50), default="pending")                  # pending/success/failed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)     # создано
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )                                                                                   # обновлено
