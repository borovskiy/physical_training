from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON

from app.db.base import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)                  # ID упражнения
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))      # владелец
    title: Mapped[str] = mapped_column(String(200))                                        # название
    type: Mapped[str] = mapped_column(String(50), default="strength")                      # тип: strength/cardio/stretch
    description: Mapped[Optional[str]] = mapped_column(Text)                               # описание выполнения
    media_url: Mapped[Optional[str]] = mapped_column(String(255))                          # ссылка на картинку/видео
    meta: Mapped[Optional[dict]] = mapped_column(JSON)                                     # доп. данные (мышцы, длительность)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)        # создано
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )                                                                                      # обновлено

    # связи
    owner: Mapped["User"] = relationship(back_populates="exercises")
    workout_items: Mapped[List["WorkoutExercise"]] = relationship(back_populates="exercise", cascade="all, delete-orphan")
