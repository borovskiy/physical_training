from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey

from app.db.base import BaseModel


class WorkoutExerciseModel(BaseModel):
    __tablename__ = "workout_exercises"

    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id", ondelete="CASCADE"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="RESTRICT"))

    position: Mapped[int] = mapped_column(default=1)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    workouts: Mapped["WorkoutModel"] = relationship(back_populates="workout_exercise")
    exercises: Mapped["ExerciseModel"] = relationship(back_populates="workouts_exercises")


