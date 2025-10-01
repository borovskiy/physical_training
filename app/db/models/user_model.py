import enum
import os
from dataclasses import dataclass

from typing import List
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Enum, Date

from db.base import BaseModel


@dataclass(frozen=True)
class PlanLimits:
    groups_limit: int
    exercises_limit: int
    workouts_limit: int
    members_group_limit: int

    @staticmethod
    def env_int(key: str, default: int):
        v = os.environ.get(key)
        try:
            return int(v) if v is not None else default
        except ValueError:
            return default


class PlanEnum(enum.Enum):
    free = "free"
    pro = "pro"


class TypeTokensEnum(enum.Enum):
    email_verify = "email_verify"
    access = "access"


class UserModel(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    password_hash: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    birth_data: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    plan: Mapped[PlanEnum] = mapped_column(Enum(PlanEnum, name="plan_enum"), default=PlanEnum.free, nullable=False)

    exercises: Mapped[List["ExerciseModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    workouts: Mapped[List["WorkoutModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    group_creator: Mapped[List["GroupModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    groups: Mapped[List["GroupModel"]] = relationship(secondary="association_group_members", back_populates="members",
                                                      overlaps="groups_members")
    groups_members: Mapped[List["GroupMemberModel"]] = relationship(back_populates="user", overlaps="groups")
    token: Mapped["JWTToken"] = relationship(back_populates="user")
