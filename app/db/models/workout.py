from __future__ import annotations
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, ForeignKey

from app.db.base import Base


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)                 # ID тренировки
    title: Mapped[str] = mapped_column(String(200), default="")                            # название тренировки
    description: Mapped[Optional[str]] = mapped_column(Text)                               # описание/заметки

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))       # кто создал
    user: Mapped["User"] = relationship(back_populates="workouts")                         # связь с владельцем

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)        # создано
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )                                                                                      # обновлено

    items: Mapped[List["WorkoutExercise"]] = relationship(
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.position",
    )                                                                                      # список упражнений (с деталями)

    exercises: Mapped[List["Exercise"]] = relationship(
        secondary="workout_exercises", viewonly=True
    )                                                                                      # просто список упражнений (viewonly)
