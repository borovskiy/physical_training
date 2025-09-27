from __future__ import annotations
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from db.base import BaseModel


class GroupModel(BaseModel):
    __tablename__ = "groups"
    name: Mapped[str] = mapped_column(String(200))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id", ondelete="CASCADE"), nullable=True)

    user: Mapped["UserModel"] = relationship(back_populates="group_creator")
    workout: Mapped["WorkoutModel"] = relationship(back_populates="groups")

    groups_members: Mapped[List["GroupMemberModel"]] = relationship(back_populates="group", overlaps="groups")
    members: Mapped[List["UserModel"]] = relationship(secondary="association_group_members", back_populates="groups",
                                                      overlaps="groups_members")


class GroupMemberModel(BaseModel):
    __tablename__ = "association_group_members"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    group: Mapped["GroupModel"] = relationship(back_populates="groups_members", overlaps="groups,members")
    user: Mapped["UserModel"] = relationship(back_populates="groups_members", overlaps="groups,members")
