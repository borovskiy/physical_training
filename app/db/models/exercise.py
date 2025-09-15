from typing import List, Optional
from datetime import datetime, timezone

from fastapi import UploadFile
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON

from app.db.base import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # ID упражнения
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))  # создано
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )  # обновлено

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))  # владелец
    title: Mapped[str] = mapped_column(String(200))  # название
    type: Mapped[str] = mapped_column(String(50), default="strength")  # тип: strength/cardio/stretch
    description: Mapped[Optional[str]] = mapped_column(Text)  # описание выполнения
    media_url: Mapped[Optional[str]] = mapped_column(String(255))  # ссылка на картинку/видео
    meta: Mapped[Optional[dict]] = mapped_column(JSON)  # доп. данные (мышцы, длительность)

    time_work: Mapped[Optional[int]] = mapped_column(default=None)  # время выполнения (сек)
    repetitions: Mapped[Optional[int]] = mapped_column(default=None)  # количество повторов (одно приседание)
    count_sets: Mapped[Optional[int]] = mapped_column(default=None)  # количество сетов(10 приседаний один сет)
    rest_sec: Mapped[Optional[int]] = mapped_column(default=None)  # пауза после (сек)

    # связи
    owner: Mapped["User"] = relationship(back_populates="exercises")
    workout_items: Mapped[List["WorkoutExercise"]] = relationship(back_populates="exercise",
                                                                  cascade="all, delete-orphan")

    def get_media_url_path(self, file: UploadFile) -> str:
        return f"{self.owner_id}/exercise_file/{self.id}/{file.filename}"

    def get_key_media_url_path_old(self) -> str | None:
        return self.media_url and self.media_url.split("/", 4)[-1]
