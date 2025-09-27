from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, JSON

from db.base import BaseModel


class ExerciseModel(BaseModel):
    __tablename__ = "exercises"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    title: Mapped[str] = mapped_column(String(200))
    type: Mapped[str] = mapped_column(String(50), default="strength")
    description: Mapped[Optional[str]] = mapped_column(Text)
    media_url: Mapped[Optional[str]] = mapped_column(String(255))
    meta: Mapped[Optional[dict]] = mapped_column(JSON)
    time_work: Mapped[Optional[int]] = mapped_column(default=None)
    repetitions: Mapped[Optional[int]] = mapped_column(default=None)
    count_sets: Mapped[Optional[int]] = mapped_column(default=None)
    rest_sec: Mapped[Optional[int]] = mapped_column(default=None)

    user: Mapped["UserModel"] = relationship(back_populates="exercises", passive_deletes=True)

    workout_exercises: Mapped[List["WorkoutExerciseModel"]] = relationship(back_populates="exercise",
                                                                           overlaps="exercises", passive_deletes=True)
    workouts: Mapped[List["WorkoutModel"]] = relationship(secondary="association_workout_exercises",
                                                          back_populates="exercises", overlaps="workout_exercises",
                                                          passive_deletes=True)

    def get_media_url_path(self, file: UploadFile) -> str:
        return f"{self.user_id}/exercise_file/{self.id}/{file.filename}"

    def get_key_media_url_path_old(self) -> str | None:
        return (self.media_url or "").rsplit("/", 1)[-1] or None

    def get_key(self, filename: str) -> str | None:
        return f"{self.user_id}/exercise_file/{self.id}/{filename}"
