from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, ForeignKey, Integer

from db.base import BaseModel


class InviteModel(BaseModel):
    __tablename__ = "invites"

    email: Mapped[str] = mapped_column(String(255))
    token: Mapped[str] = mapped_column(String(255), unique=True)  # токен (JWT/UUID)
    invited_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(50), default="pending")
