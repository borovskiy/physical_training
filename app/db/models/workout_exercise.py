from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text, ForeignKey

from app.db.base import Base


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)                      # ID строки
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id", ondelete="CASCADE"))     # к какой тренировке
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="RESTRICT"))  # какое упражнение

    position: Mapped[int] = mapped_column(default=1)                                           # порядок в воркауте
    reps: Mapped[Optional[int]] = mapped_column()                                              # количество повторов
    rest_sec: Mapped[Optional[int]] = mapped_column()                                          # пауза после (сек)
    notes: Mapped[Optional[str]] = mapped_column(Text)                                         # комментарии

    workout: Mapped["Workout"] = relationship(back_populates="items")                          # связь с воркаутом
    exercise: Mapped["Exercise"] = relationship(back_populates="workout_items")                # связь с упражнением
