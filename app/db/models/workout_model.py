from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey

from db.base import BaseModel


class WorkoutModel(BaseModel):
    __tablename__ = "workouts"
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["UserModel"] = relationship(back_populates="workouts")

    groups: Mapped[List["GroupModel"]] = relationship(back_populates="workout", cascade="all, delete-orphan")

    workout_exercises: Mapped[List["WorkoutExerciseModel"]] = relationship(back_populates="workout",
                                                                           cascade="all, delete-orphan",
                                                                           order_by="WorkoutExerciseModel.position",
                                                                           overlaps="workouts",
                                                                           passive_deletes=True)

    exercises: Mapped[List["ExerciseModel"]] = relationship(secondary="association_workout_exercises",
                                                            back_populates="workouts", overlaps="workout_exercises")


class WorkoutExerciseModel(BaseModel):
    __tablename__ = "association_workout_exercises"

    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id", ondelete="CASCADE"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"))

    position: Mapped[int] = mapped_column(default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    workout: Mapped["WorkoutModel"] = relationship(back_populates="workout_exercises", overlaps="workouts,exercises",
                                                   passive_deletes=True)
    exercise: Mapped["ExerciseModel"] = relationship(back_populates="workout_exercises", overlaps="workouts,exercises",
                                                     passive_deletes=True)
