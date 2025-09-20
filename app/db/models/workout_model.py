from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey

from app.db.base import BaseModel


class WorkoutModel(BaseModel):
    __tablename__ = "workouts"
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["UserModel"] = relationship(back_populates="workouts")

    groups: Mapped[List["GroupModel"]] = relationship(back_populates="workout", cascade="all, delete-orphan")

    exercises: Mapped[List["ExerciseModel"]] = relationship(secondary="association_workout_exercises",
                                                            back_populates="workouts")
    workout_exercises: Mapped[List["WorkoutExerciseModel"]] = relationship(back_populates="workout",
                                                                           order_by="WorkoutExerciseModel.position",
                                                                           )


class WorkoutExerciseModel(BaseModel):
    __tablename__ = "association_workout_exercises"

    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))

    position: Mapped[int] = mapped_column(default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    workout: Mapped["WorkoutModel"] = relationship(back_populates="workout_exercises")
    exercise: Mapped["ExerciseModel"] = relationship(back_populates="workout_exercises")
