from typing import List, Sequence

from db.schemas.base import BaseIdSchema, BaseModelSchema, BaseCreatedAndUpdateSchema
from db.schemas.paginate import PageMeta


class WorkoutExerciseCreateSchema(BaseModelSchema):
    exercise_id: int
    position: int


class WorkoutCreateSchema(BaseModelSchema):
    title: str
    description: str


class ExerciseFullSchema(BaseIdSchema, BaseCreatedAndUpdateSchema, BaseModelSchema):
    title: str
    type: str
    media_url: str | None
    rest_sec: int
    description: str

    count_sets: int | None

    repetitions: int | None
    time_work: int | None


class WorkoutExerciseFullSchema(BaseIdSchema,BaseCreatedAndUpdateSchema, BaseModelSchema):
    exercises: ExerciseFullSchema
    position: int


class WorkoutGetOneSchema(BaseIdSchema, BaseCreatedAndUpdateSchema, WorkoutCreateSchema):
    pass


class WorkoutFullSchema(WorkoutGetOneSchema):
    workout_exercise: List[WorkoutExerciseFullSchema]


class WorkoutPage(BaseModelSchema):
    workouts: Sequence[WorkoutGetOneSchema]
    meta: PageMeta
