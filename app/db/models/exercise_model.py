from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, JSON

from app.db.base import BaseModel


class ExerciseModel(BaseModel):
    __tablename__ = "exercises"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))  # владелец

    title: Mapped[str] = mapped_column(String(200))  # название
    type: Mapped[str] = mapped_column(String(50), default="strength")  # тип: strength/cardio/stretch
    description: Mapped[Optional[str]] = mapped_column(Text)  # описание выполнения
    media_url: Mapped[Optional[str]] = mapped_column(String(255))  # ссылка на картинку/видео
    meta: Mapped[Optional[dict]] = mapped_column(JSON)  # доп. данные (мышцы, длительность)
    time_work: Mapped[Optional[int]] = mapped_column(default=None)  # время выполнения (сек)
    repetitions: Mapped[Optional[int]] = mapped_column(default=None)  # количество повторов (одно приседание)
    count_sets: Mapped[Optional[int]] = mapped_column(default=None)  # количество сетов(10 приседаний один сет)
    rest_sec: Mapped[Optional[int]] = mapped_column(default=None)  # пауза после (сек)

    user: Mapped["UserModel"] = relationship(back_populates="exercises")

    workout_exercises: Mapped[List["WorkoutExerciseModel"]] = relationship(back_populates="exercise",
                                                                           overlaps="exercises")
    workouts: Mapped[List["WorkoutModel"]] = relationship(secondary="association_workout_exercises",
                                                          back_populates="exercises", overlaps="workout_exercises")

    def get_media_url_path(self, file: UploadFile) -> str:
        return f"{self.user_id}/exercise_file/{self.id}/{file.filename}"

    def get_key_media_url_path_old(self) -> str | None:
        return (self.media_url or "").rsplit("/", 1)[-1] or None
