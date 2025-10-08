from math import ceil
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_limits
from db.models import WorkoutModel
from db.schemas.paginate_schema import PageMeta
from db.schemas.workout_schema import WorkoutCreateSchema, WorkoutExerciseCreateSchema, WorkoutPage
from repositories.exercise_repositories import ExerciseRepository
from repositories.user_repository import UserRepository
from repositories.workout_repositories import WorkoutRepository
from services.base_services import BaseServices
from utils.context import get_current_user
from utils.raises import _forbidden, _not_found
from utils.workout_utils import get_list_set_exercises_schema, check_belonging_exercise_on_user


class WorkoutServices(BaseServices):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.repo_workout = WorkoutRepository(session)
        self.repo_exercise = ExerciseRepository(session)
        self.repo_user = UserRepository(session)

    async def get_workouts(self, limit: int, start: int, user_id: int = None):
        self.log.info("Try get all workouts repo")
        workouts, total = await self.repo_workout.get_all_workouts(
            BaseServices.check_permission(get_current_user(), user_id), limit, start)
        self.log.info("workouts %s", workouts)
        self.log.info("total %s", total)
        pages = ceil(total / limit) - 1 if limit else 1
        self.log.info("pages %s", pages)
        return WorkoutPage(
            workouts=workouts,
            meta=PageMeta(total=total, limit=limit, pages=pages),
        )

    async def get_workout_id(self, workout_id: int) -> WorkoutModel:
        current_user = get_current_user()
        self.log.info("Try get workout id")
        workout = await self.repo_workout.get_workout_for_user(workout_id, current_user.id, get_current_user().is_admin)
        self.log.info("workout id %s", workout_id)
        return workout

    async def update_workout(self, workout_id: int, workout_schema: WorkoutExerciseCreateSchema) -> WorkoutModel:
        self.log.info("update_workout")
        workout = await self.repo_workout.get_workout_for_user(workout_id, get_current_user().id,
                                                               get_current_user().is_admin)
        list_id_exercise = await get_list_set_exercises_schema(workout_schema.exercises)
        count_self_exercise = await self.repo_exercise.find_count_self_exercise(workout.user_id, list_id_exercise)
        await check_belonging_exercise_on_user(count_self_exercise, list_id_exercise)
        result_workout = await self.repo_workout.update_workout(workout_id, workout.user_id, workout_schema)
        return await self.get_workout_id(result_workout.id)

    async def create_workout(self, workout_schema: WorkoutExerciseCreateSchema, user_id: int = None) -> WorkoutModel:
        self.log.info("create_workout")
        user = await self.repo_user.find_user_id(BaseServices.check_permission(get_current_user(), user_id))
        user.check_reached_limit_workouts(await self.repo_workout.get_workout_count(user_id))
        list_id_exercise = await get_list_set_exercises_schema(workout_schema.exercises)
        count_self_exercise = await self.repo_exercise.find_count_self_exercise(user_id, list_id_exercise)
        await check_belonging_exercise_on_user(count_self_exercise, list_id_exercise)
        result_workout = await self.repo_workout.add_workout(workout_schema.workout.model_dump(),
                                                             workout_schema.exercises,
                                                             user_id)
        return await self.get_workout_id(result_workout.id)

    async def remove_workout(self, workout_id: int):
        workout = await self.repo_workout.get_workout_for_user(workout_id, get_current_user().id,
                                                               get_current_user().is_admin)
        result = await self.repo_workout.remove_workout_id(workout)
        return result
