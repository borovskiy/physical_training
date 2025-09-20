from typing import Optional, Dict, Any, Sequence

from fastapi import Form

from db.models import ExerciseModel
from db.schemas.base_schema import BaseModelSchema, BaseIdSchema, BaseCreatedAndUpdateSchema
from db.schemas.paginate_schema import PageMeta


class ExerciseSchema(BaseModelSchema, BaseIdSchema, BaseCreatedAndUpdateSchema):
    user_id: int
    title: str
    type: str
    description: str
    media_url: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None



class UpdateExerciseSchema(BaseModelSchema):
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


class ExercisePage(BaseModelSchema):
    exercise: Sequence[ExerciseSchema]
    meta: PageMeta
