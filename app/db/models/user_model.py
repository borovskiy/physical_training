import enum
import os
from dataclasses import dataclass

from typing import List
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Enum, Date

from core.config import get_limits
from db.base import BaseModel
from utils.context import get_current_user
from utils.raises import _forbidden


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
    token: Mapped["JWTTokenModel"] = relationship(back_populates="user")

    def get_limits(self) -> PlanLimits:
        return get_limits(self.plan)

    def check_reached_limit_workouts(self, count_workouts: int) -> bool:
        # the administrator has the right to create objects without limits
        if count_workouts >= self.get_limits().workouts_limit and get_current_user().is_not_admin():
            raise _forbidden("You have reached the limit for creating workouts.")
        return False

    def check_reached_limit_exercises(self, count_exercises: int) -> bool:
        # the administrator has the right to create objects without limits
        if count_exercises >= self.get_limits().exercises_limit and get_current_user().is_not_admin():
            raise _forbidden("You have reached the limit for creating exercise.")
        return False

    def check_reached_limit_group(self, count_groups: int) -> bool:
        # the administrator has the right to create objects without limits
        if count_groups >= self.get_limits().groups_limit and get_current_user().is_not_admin():
            raise _forbidden("You cannot add more users to this group")
        return False
