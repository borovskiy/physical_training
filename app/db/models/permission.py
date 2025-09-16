from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer

from app.db.base import BaseModel


class PermissionModel(BaseModel):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resource_type: Mapped[str] = mapped_column(String(50))
    resource_id: Mapped[int] = mapped_column()
    grantee_type: Mapped[str] = mapped_column(String(20))
    grantee_id: Mapped[Optional[int]] = mapped_column()
    scopes: Mapped[str] = mapped_column(String(100))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
