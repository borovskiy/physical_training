from typing import List

from db.schemas.workout_schema import WorkoutExerciseCreateSchema
from utils.raises import _forbidden


async def get_list_set_exercises_schema(exercise_schemas: List[WorkoutExerciseCreateSchema]) -> list[int]:
    return list(set([i.exercise_id for i in exercise_schemas]))


async def check_belonging_exercise_on_user(count_self_exercise: int, list_id_exercise: List[int]):
    if count_self_exercise != len(list_id_exercise):
        raise _forbidden("You do not have the right to use gestures that do not belong to you.")
