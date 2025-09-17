import enum
from typing import List
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, Enum

from app.db.base import BaseModel


class PlanEnum(enum.Enum):
    free = "free"
    pro = "pro"


class UserModel(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    password_hash: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    birth_data: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    plan: Mapped[PlanEnum] = mapped_column(Enum(PlanEnum, name="plan_enum"), default=PlanEnum.free, nullable=False)

    exercises: Mapped[List["ExerciseModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    workouts: Mapped[List["WorkoutModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    groups: Mapped[List["GroupModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    members: Mapped[List["GroupMemberModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")


