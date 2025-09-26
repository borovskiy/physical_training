from typing import List, Sequence

from pydantic import model_validator

from app.db.schemas.base_schema import BaseIdSchema, BaseModelSchema, BaseCreatedAndUpdateSchema
from app.db.schemas.paginate_schema import PageMeta


class ExerciseCreateSchema(BaseModelSchema):
    exercise_id: int
    position: int


class WorkoutCreateSchema(BaseModelSchema):
    title: str
    description: str


class WorkoutExerciseCreateSchema(BaseModelSchema):
    workout: WorkoutCreateSchema
    exercises: List[ExerciseCreateSchema]

    @model_validator(mode="after")
    def positions_must_be_consecutive(self):
        positions = [it.position for it in self.exercises]
        n = len(positions)
        if n == 0:
            return self
        if any(p < 1 for p in positions):
            raise ValueError("All 'position' values must be >= 1.")
        if set(positions) != set(range(1, n + 1)):
            missing = sorted(set(range(1, n + 1)) - set(positions))
            dups = sorted({p for p in positions if positions.count(p) > 1})
            extra = ""
            if missing:
                extra += f" missing: {missing}"
            if dups:
                extra += f" duplicates: {dups}"
            raise ValueError(
                "The 'position' fields must form a consecutive sequence 1..N with no gaps or duplicates." + extra
            )
        return self


class ExerciseFullSchema(BaseIdSchema, BaseCreatedAndUpdateSchema, BaseModelSchema):
    title: str
    type: str
    media_url: str | None
    rest_sec: int
    description: str

    count_sets: int | None

    repetitions: int | None
    time_work: int | None


class WorkoutExerciseFullSchema(BaseModelSchema):
    exercise: ExerciseFullSchema
    position: int


class WorkoutGetOneSchema(BaseIdSchema, BaseCreatedAndUpdateSchema, WorkoutCreateSchema):
    pass


class WorkoutFullSchema(WorkoutGetOneSchema):
    workout_exercises: List[WorkoutExerciseFullSchema]


class WorkoutPage(BaseModelSchema):
    workouts: List[WorkoutGetOneSchema]
    meta: PageMeta
