import logging
from math import ceil

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_limits
from core.s3_cloud_connector import S3CloudConnector
from db.models import ExerciseModel
from db.schemas.exercise_schema import CreateExerciseSchema, ExercisePage, PageMeta, UpdateExerciseSchema
from repositories.exercise_repositories import ExerciseRepository
from utils.context import get_current_user
from utils.raises import _forbidden, _not_found

logger = logging.getLogger(__name__)


class ExerciseServices:
    def __init__(self, session: AsyncSession):
        self.repo = ExerciseRepository(session)
        self.s3 = S3CloudConnector()

    async def get_exercises(self, limit: int, start: int) -> ExercisePage:
        logger.info("Try get exercises")
        current_user = get_current_user()
        exercises, total = await self.repo.get_all_exercise_user(current_user.id, limit, start)
        logger.info("exercises %s", exercises)
        logger.info("total %s", total)
        pages = ceil(total / limit) if limit else 1
        return ExercisePage(
            exercises=exercises,
            meta=PageMeta(total=total, limit=limit, pages=pages),
        )

    async def get_exercise(self, exercise_id: int) -> ExerciseModel:
        logger.info("Try get exercise")
        current_user = get_current_user()
        exercise = await self.repo.get_by_id(current_user.id, exercise_id)
        logger.info("exercise %s", exercise)
        if exercise is None:
            logger.error("No exercise found")
            raise _not_found("No exercise found")
        return exercise

    async def add_exercise(self, payload: CreateExerciseSchema, file: UploadFile) -> ExerciseModel:
        logger.info("add exercise data %s", payload.model_dump())
        current_user = get_current_user()
        if await self.repo.get_count_exercise_user(current_user.id) >= get_limits(current_user.plan).exercises_limit:
            logger.error("You have reached the limit for creating exercise.")
            raise _forbidden("You have reached the limit for creating exercise.")

        new_exercise = await self.repo.add_exercise(payload.model_dump(), current_user.id)
        logger.info("New exercise %s", new_exercise)
        logger.info("Try upload file")
        link_exercise = await self.s3.upload_upload_file(self.s3.bucket, new_exercise.get_media_url_path(file), file,
                                                         True)
        logger.info("link exercise %s", link_exercise)
        new_exercise = await self.repo.update_link_exercise(new_exercise.id, link_exercise)
        logger.info("New exercise %s", new_exercise)
        return new_exercise

    async def update_exercise(self, exercise_id: int, schema: UpdateExerciseSchema) -> ExerciseModel:
        logger.info("update exercise id %s", exercise_id)
        current_user = get_current_user()
        exercise = await self.repo.get_by_id(current_user.id, exercise_id)
        logger.info("exercise %s", exercise)
        if exercise is None:
            logger.error("No exercise found")
            raise _forbidden("No exercise found")
        new_exercise = await self.repo.update_exercise(schema.model_dump(), current_user.id, exercise_id)
        logger.info("New exercise %s", new_exercise)
        return new_exercise

    async def update_file_exercise(self, exercise_id: int, file: UploadFile) -> ExerciseModel | None:
        logger.info("update file exercise id %s", exercise_id)
        current_user = get_current_user()
        exercise = await self.repo.get_by_id(current_user.id, exercise_id)
        logger.info("exercise %s", exercise)
        if exercise is not None:
            link_for_remove = exercise.get_key_media_url_path_old()
            logger.info("old link %s", link_for_remove)
            name_key_file = exercise.get_media_url_path(file)
            logger.info("name key file %s", name_key_file)
            link_exercise = await self.s3.upload_upload_file(self.s3.bucket, name_key_file, file, True)
            logger.info("new link exercise %s", link_exercise)
            new_exercise = await self.repo.update_link_exercise(exercise_id, link_exercise)
            if link_for_remove != name_key_file and link_for_remove is not None:
                await self.s3.remove_file_url(self.s3.bucket, link_for_remove)
            return new_exercise
        else:
            logger.error("No exercise found")
            return _forbidden("No exercise found")

    async def remove_exercise_from_all_workout(self, exercise_id: int) -> ExerciseModel:
        logger.info("remove exercise from all workout id %s", exercise_id)
        current_user = get_current_user()
        exercise = await self.repo.get_by_id(current_user.id, exercise_id)
        logger.info("exercise %s", exercise)
        if exercise is None:
            logger.error("No exercise found")
            _forbidden("No exercise found")
        logger.info("remove file url")
        await self.s3.remove_file_url(self.s3.bucket, exercise.get_key_media_url_path_old())
        logger.info("remove exercise id")
        await self.repo.remove_exercise_id(exercise_id)
        return exercise
