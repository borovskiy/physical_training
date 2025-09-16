from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, ForeignKey, Integer

from app.db.base import BaseModel


class InviteModel(BaseModel):
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)                 # ID инвайта
    email: Mapped[str] = mapped_column(String(255))                                       # кого приглашаем
    token: Mapped[str] = mapped_column(String(255), unique=True)                          # токен (JWT/UUID)
    invited_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))   # кто пригласил
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id"))              # если сразу в группу
    expires_at: Mapped[datetime] = mapped_column(DateTime)                                # срок действия
    status: Mapped[str] = mapped_column(String(50), default="pending")                    # pending/accepted/expired
