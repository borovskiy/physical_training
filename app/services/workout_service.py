import logging
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
from utils.workout_utils import get_list_set_exercises_schema, check_belonging_exercise_on_user

logger = logging.getLogger(__name__)


class WorkoutServices:
    def __init__(self, session: AsyncSession):
        self.repo_workout = WorkoutRepository(session)
        self.repo_workout_exercise = WorkoutExerciseRepository(session)
        self.repo_exercise = ExerciseRepository(session)

    async def get_workouts(self, limit: int, start: int):
        current_user = get_current_user()
        logger.info("Try get all workouts repo")
        workouts, total = await self.repo_workout.get_all_workouts(current_user.id, limit, start)
        logger.info("workouts %s", workouts)
        logger.info("total %s", total)
        pages = ceil(total / limit) - 1 if limit else 1
        logger.info("pages %s", pages)
        return WorkoutPage(
            workouts=workouts,
            meta=PageMeta(total=total, limit=limit, pages=pages),
        )

    async def get_workout_id(self, workout_id: int) -> WorkoutModel:
        current_user = get_current_user()
        logger.info("Try get workout id")
        workout = await self.repo_workout.get_workout_with_user(workout_id, current_user.id)
        logger.info("workout %s", workout)
        if workout is None:
            logger.error("No workout found id %s", workout_id)
            raise _not_found("No workout found")
        return workout

    async def update_workout(self, workout_id: int,
                             exercises_schema: List[WorkoutExerciseCreateSchema]) -> WorkoutModel:
        current_user = get_current_user()
        logger.info("Try update workout id %s", workout_id)
        list_id_exercise = await get_list_set_exercises_schema(exercises_schema)
        logger.info("list id exercise %s", list_id_exercise)
        count_self_exercise = await self.repo_exercise.find_count_self_exercise(current_user.id, list_id_exercise)
        logger.info("count exercise %s", count_self_exercise)
        await check_belonging_exercise_on_user(count_self_exercise, list_id_exercise)

        await self.repo_workout.update_workout(workout_id, current_user.id, exercises_schema)
        return await self.get_workout_id(workout_id)

    async def create_workout(self, workout_schema: WorkoutCreateSchema,
                             exercises_schema: List[WorkoutExerciseCreateSchema]) -> WorkoutModel:
        current_user = get_current_user()
        list_id_exercise = await get_list_set_exercises_schema(exercises_schema)
        count_self_exercise = await self.repo_exercise.find_count_self_exercise(current_user.id, list_id_exercise)
        await check_belonging_exercise_on_user(count_self_exercise, list_id_exercise)

        if await self.repo_workout.get_workout_count(current_user.id) >= get_limits(current_user.plan).workouts_limit:
            raise _forbidden("You have reached the limit for creating workouts.")
        result_workout = await self.repo_workout.add_workout(workout_schema.model_dump(), exercises_schema,
                                                             current_user.id)
        return await self.get_workout_id(result_workout.id)

    async def remove_workout(self, workout_id: int):
        current_user = get_current_user()
        workout = await self.repo_workout.get_workout_with_user(workout_id, current_user.id)
        if workout is None:
            raise _forbidden("No workout found")
        result = await self.repo_workout.remove_workout_id(workout)
        return result
