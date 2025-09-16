from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, ForeignKey

from app.db.base import BaseModel


class WorkoutModel(BaseModel):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[Optional[str]] = mapped_column(Text)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )
    user: Mapped["UserModel"] = relationship(back_populates="workouts")

    items: Mapped[List["WorkoutExerciseModel"]] = relationship(
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="WorkoutExerciseModel.position",
    )

    exercises: Mapped[List["ExerciseModel"]] = relationship(
        secondary="workout_exercises", viewonly=True
    )
