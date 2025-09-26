from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey

from app.db.base import BaseModel


class BillingTransactionModel(BaseModel):
    __tablename__ = "billing_transactions"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))  # чей платёж
    provider: Mapped[str] = mapped_column(String(50), default="stripe")  # провайдер (stripe и т.д.)
    external_id: Mapped[str] = mapped_column(String(255))  # ID у провайдера
    amount_cents: Mapped[int] = mapped_column()  # сумма (в центах)
    currency: Mapped[str] = mapped_column(String(10), default="USD")  # валюта
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending/success/failed
