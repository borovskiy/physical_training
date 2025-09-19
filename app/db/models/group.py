from __future__ import annotations
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from app.db.base import BaseModel


class GroupModel(BaseModel):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))

    user: Mapped["UserModel"] = relationship(back_populates="groups")
    members: Mapped[List["GroupMemberModel"]] = relationship(back_populates="group", cascade="all, delete-orphan")


class GroupMemberModel(BaseModel):
    __tablename__ = "group_members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id", ondelete="CASCADE"), nullable=True)

    group: Mapped["GroupModel"] = relationship(back_populates="members")
    user: Mapped["UserModel"] = relationship(back_populates="members")
    workout: Mapped["WorkoutModel"] = relationship(back_populates="group_members")
