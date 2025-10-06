from typing import Optional, Sequence

from fastapi import Form, HTTPException
from pydantic import PrivateAttr

from db.schemas.base_schema import BaseModelSchema, BaseIdSchema, BaseCreatedAndUpdateSchema
from db.schemas.paginate_schema import PageMeta
from db.schemas.workout_schema import ExerciseFullSchema


class UpdateExerciseSchema(BaseModelSchema):
    title: str
    type: str
    description: str


class CreateExerciseSchema(UpdateExerciseSchema):
    time_work: Optional[int] = None
    repetitions: Optional[int] = None
    count_sets: Optional[int] = None
    rest_sec: Optional[int]
    _user_id: int | None = PrivateAttr(default=None)  # приватное поле, не видно снаружи

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if self._user_id is not None:
            data["user_id"] = self._user_id
        return data


def _to_int_or_none(v: Optional[int], field: int) -> Optional[int]:
    if v is None:
        return None
    try:
        return v
    except ValueError:
        raise HTTPException(status_code=422, detail=f"{field} must be an integer")


def parse_create_exercise_form(
        title: str = Form(...),
        type: str = Form(...),
        description: str = Form(...),
        time_work: Optional[int] = Form(None),
        repetitions: Optional[int] = Form(None),
        count_sets: Optional[int] = Form(None),
        rest_sec: Optional[int] = Form(None),
) -> CreateExerciseSchema:
    tw = _to_int_or_none(time_work, "time_work")
    rep = _to_int_or_none(repetitions, "repetitions")
    cs = _to_int_or_none(count_sets, "count_sets")
    rs = _to_int_or_none(rest_sec, "rest_sec")

    has_time = tw is not None
    has_reps_sets = (rep is not None) and (cs is not None)

    if not has_time and not has_reps_sets:
        raise HTTPException(
            status_code=422,
            detail="Specify either time_work or both field repetitions and count_sets."
        )
    # сделать взаимоисключающим режим — оставьте блок; если допускаете оба — уберите.
    if has_time and (rep is not None or cs is not None):
        raise HTTPException(
            status_code=422,
            detail="Select one mode: time_work only OR (repetitions + count_sets)."
        )

    return CreateExerciseSchema(
        title=title, type=type, description=description,
        time_work=tw, repetitions=rep, count_sets=cs, rest_sec=rs
    )


class ExercisePage(BaseModelSchema):
    meta: PageMeta
    exercises: Sequence[ExerciseFullSchema]
