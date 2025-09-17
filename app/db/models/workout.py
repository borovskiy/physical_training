from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey

from app.db.base import BaseModel


class WorkoutModel(BaseModel):
    __tablename__ = "workouts"
    title: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[Optional[str]] = mapped_column(Text)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["UserModel"] = relationship(back_populates="workouts")
    workout_exercise: Mapped[List["WorkoutExerciseModel"]] = relationship(
        back_populates="workouts",
        cascade="all, delete-orphan",
        order_by="WorkoutExerciseModel.position",
    )
    exercises: Mapped[List["ExerciseModel"]] = relationship(secondary="workout_exercises", viewonly=True)
