from datetime import datetime
from typing import Optional, Dict, Any, List, Sequence

from fastapi import Form, UploadFile, File
from pydantic import BaseModel, ConfigDict

from db.schemas.paginate import PageMeta


class ExerciseSchema(BaseModel):
    id: int
    owner_id: int
    title: str
    type: str
    description: str
    media_url: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None  # <-- допускаем None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpdateExerciseSchema(BaseModel):
    title: str
    type: str
    description: str


class CreateExerciseSchema(UpdateExerciseSchema):

    @classmethod
    def as_form(
            cls,
            title: str = Form(...),
            type: str = Form(...),
            description: str = Form(...),
    ):
        return cls(
            title=title,
            type=type,
            description=description,
        )


class ExercisePage(BaseModel):
    exercise: Sequence[ExerciseSchema]
    meta: PageMeta
