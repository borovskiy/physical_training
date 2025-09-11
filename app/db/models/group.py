from __future__ import annotations
from typing import List
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Integer, ForeignKey

from app.db.base import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)                    # ID группы
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))        # создатель группы
    name: Mapped[str] = mapped_column(String(200))                                           # название группы
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)          # создана

    owner: Mapped["User"] = relationship(back_populates="groups")                            # ссылка на владельца
    members: Mapped[List["GroupMember"]] = relationship(back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "group_members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)                    # ID строки
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))       # группа
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))         # участник

    group: Mapped["Group"] = relationship(back_populates="members")                          # связь на группу
