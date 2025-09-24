from math import ceil
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_limits
from db.models import WorkoutModel
from db.schemas.paginate_schema import PageMeta
from db.schemas.workout_schema import WorkoutCreateSchema, WorkoutExerciseCreateSchema, WorkoutPage
from repositories.exercise_repositories import ExerciseRepository
from repositories.workout_exercise_repository import WorkoutExerciseRepository
from repositories.workout_repositories import WorkoutRepository
from utils.context import get_current_user
from utils.raises import _forbidden, _not_found


class WorkoutServices:
    def __init__(self, session: AsyncSession):
        self.repo_workout = WorkoutRepository(session)
        self.repo_workout_exercise = WorkoutExerciseRepository(session)
        self.repo_exercise = ExerciseRepository(session)

    async def get_workouts(self, limit: int, start: int):
        current_user = get_current_user()
        workouts, total = await self.repo_workout.get_all_workouts(current_user.id, limit, start)
        pages = ceil(total / limit) - 1 if limit else 1
        return WorkoutPage(
            workouts=workouts,
            meta=PageMeta(total=total, limit=limit, pages=pages),
        )

    async def get_workout_id(self, workout_id: int) -> WorkoutModel:
        current_user = get_current_user()

        workout = await self.repo_workout.get_workout_with_user(workout_id, current_user.id)
        if workout is None:
            raise _not_found("No workout found")
        return workout

    async def create_workout(self, workout_schema: WorkoutCreateSchema,
                             exercises_schema: List[WorkoutExerciseCreateSchema]) -> WorkoutModel:
        current_user = get_current_user()
        list_id_exercise = list(set([i.exercise_id for i in exercises_schema]))
        count_self_exercise = await self.repo_exercise.find_count_self_exercise(current_user.id, list_id_exercise)
        if count_self_exercise != len(list_id_exercise):
            raise _forbidden("You do not have the right to use gestures that do not belong to you.")
        if await self.repo_workout.get_workout_count(current_user.id) >= get_limits(current_user.plan).workouts_limit:
            raise _forbidden("You have reached the limit for creating workouts.")
        result_workout = await self.repo_workout.add_workout(workout_schema.model_dump(), current_user.id)
        await self.repo_workout_exercise.add_workout_exercise(exercises_schema, result_workout.id, current_user.id)
        return await self.get_workout_id(result_workout.id)

    async def remove_workout(self, workout_id: int):
        current_user = get_current_user()

        workout = await self.repo_workout.get_workout_with_user(current_user.id, workout_id)
        if workout is None:
            raise _forbidden("No workout found")
        result = await self.repo_workout.remove_workout_id(workout)
        return result
