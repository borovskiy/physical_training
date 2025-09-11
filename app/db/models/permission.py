from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer

from app.db.base import Base


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)               # ID доступа
    resource_type: Mapped[str] = mapped_column(String(50))                              # "exercise" | "workout"
    resource_id: Mapped[int] = mapped_column()                                          # ID ресурса
    grantee_type: Mapped[str] = mapped_column(String(20))                               # "user" | "group" | "link"
    grantee_id: Mapped[Optional[int]] = mapped_column()                                 # ID юзера/группы (NULL для link)
    scopes: Mapped[str] = mapped_column(String(100))                                    # права: "view", "view,edit"
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)                    # срок действия или NULL
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)     # когда выдан доступ
