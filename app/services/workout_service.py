from math import ceil
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, Workout
from db.schemas.paginate import PageMeta
from db.schemas.workout import WorkoutCreateSchema, WorkoutExerciseCreateSchema, WorkoutPage
from repositories.exercise_repositories import ExerciseRepository
from repositories.workout_exercise_repository import WorkoutExerciseRepository
from repositories.workout_repositories import WorkoutRepository
from services.auth_service import _forbidden


class WorkoutServices:
    def __init__(self, session: AsyncSession):
        self.repo_workout = WorkoutRepository(session)
        self.repo_workout_exercise = WorkoutExerciseRepository(session)
        self.repo_exercise = ExerciseRepository(session)

    async def create_workout(self, workout_schema: WorkoutCreateSchema,
                             exercises_schema: List[WorkoutExerciseCreateSchema], user: User) -> Workout:
        count_self_exercise = await self.repo_exercise.find_count_self_exercise(user.id, exercises_schema)
        if count_self_exercise == len(set([i.exercise_id for i in exercises_schema])):
            result_workout = await self.repo_workout.add_workout(workout_schema.model_dump(), user.id)
            await self.repo_workout_exercise.add_workout_exercise(exercises_schema, result_workout.id, user.id)
            return await self.get_workout(result_workout.id)
        else:
            raise _forbidden("You do not have the right to use gestures that do not belong to you.")

    async def get_workout(self, workout_id: int) -> Workout:
        result_workout = await self.repo_workout.get_workout(workout_id)
        return result_workout

    async def get_workouts(self, user_id: int, limit: int, start: int):
        workouts, total = await self.repo_workout.get_all_workouts(user_id, limit, start)
        pages = ceil(total / limit) - 1 if limit else 1
        return WorkoutPage(
            workouts=workouts,
            meta=PageMeta(total=total, limit=limit, pages=pages),
        )

    async def remove_workout(self, workout_id: int, user: User):
        get_workout = await self.repo_workout.get_workout_with_user(user.id, workout_id)
        if get_workout is None:
            _forbidden("No workout found")
        result = await self.repo_workout.remove_workout_id(workout_id)
        return result