from math import ceil

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_limits
from app.core.s3_cloud_connector import S3CloudConnector
from app.db.models import ExerciseModel
from app.db.schemas.exercise_schema import CreateExerciseSchema, ExercisePage, PageMeta, UpdateExerciseSchema
from app.repositories.exercise_repositories import ExerciseRepository
from app.services.base_services import BaseServices
from app.utils.context import get_current_user
from app.utils.raises import _forbidden, _not_found


class ExerciseServices(BaseServices):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.repo = ExerciseRepository(session)
        self.s3 = S3CloudConnector()

    async def get_exercises(self, limit: int, start: int) -> ExercisePage:
        self.log.info("Try get exercises")
        current_user = get_current_user()
        exercises, total = await self.repo.get_all_exercise_user(current_user.id, limit, start)
        self.log.info("exercises %s", exercises)
        self.log.info("total %s", total)
        pages = ceil(total / limit) if limit else 1
        return ExercisePage(
            exercises=exercises,
            meta=PageMeta(total=total, limit=limit, pages=pages),
        )

    async def get_exercise(self, exercise_id: int) -> ExerciseModel:
        self.log.info("Try get exercise")
        current_user = get_current_user()
        exercise = await self.repo.get_by_id(current_user.id, exercise_id)
        self.log.info("exercise %s", exercise)
        if exercise is None:
            self.log.error("No exercise found")
            raise _not_found("No exercise found")
        return exercise

    async def add_exercise(self, payload: CreateExerciseSchema, file: UploadFile) -> ExerciseModel:
        self.log.info("add exercise data %s", payload.model_dump())
        current_user = get_current_user()
        if await self.repo.get_count_exercise_user(current_user.id) >= get_limits(current_user.plan).exercises_limit:
            self.log.error("You have reached the limit for creating exercise.")
            raise _forbidden("You have reached the limit for creating exercise.")

        new_exercise = await self.repo.add_exercise(payload.model_dump(), current_user.id)
        self.log.info("New exercise %s", new_exercise)
        self.log.info("Try upload file")
        link_exercise = await self.s3.upload_upload_file(self.s3.bucket, new_exercise.get_media_url_path(file), file,
                                                         True)
        self.log.info("link exercise %s", link_exercise)
        new_exercise = await self.repo.update_link_exercise(new_exercise.id, link_exercise)
        self.log.info("New exercise %s", new_exercise)
        return new_exercise

    async def update_exercise(self, exercise_id: int, schema: UpdateExerciseSchema) -> ExerciseModel:
        self.log.info("update exercise id %s", exercise_id)
        current_user = get_current_user()
        exercise = await self.repo.get_by_id(current_user.id, exercise_id)
        self.log.info("exercise %s", exercise)
        if exercise is None:
            self.log.error("No exercise found")
            raise _forbidden("No exercise found")
        new_exercise = await self.repo.update_exercise(schema.model_dump(), current_user.id, exercise_id)
        self.log.info("New exercise %s", new_exercise)
        return new_exercise

    async def update_file_exercise(self, exercise_id: int, file: UploadFile) -> ExerciseModel | None:
        self.log.info("update file exercise id %s", exercise_id)
        current_user = get_current_user()
        exercise = await self.repo.get_by_id(current_user.id, exercise_id)
        self.log.info("exercise %s", exercise)
        if exercise is not None:
            link_for_remove = exercise.get_key_media_url_path_old()
            self.log.info("old link %s", link_for_remove)
            name_key_file = exercise.get_media_url_path(file)
            self.log.info("name key file %s", name_key_file)
            link_exercise = await self.s3.upload_upload_file(self.s3.bucket, name_key_file, file, True)
            self.log.info("new link exercise %s", link_exercise)
            new_exercise = await self.repo.update_link_exercise(exercise_id, link_exercise)
            if link_for_remove != name_key_file and link_for_remove is not None:
                await self.s3.remove_file_url(self.s3.bucket, new_exercise.get_key(link_for_remove))
            return new_exercise
        else:
            self.log.error("No exercise found")
            return _forbidden("No exercise found")

    async def remove_exercise_from_all_workout(self, exercise_id: int) -> ExerciseModel:
        self.log.info("remove exercise from all workout id %s", exercise_id)
        current_user = get_current_user()
        exercise = await self.repo.get_by_id(current_user.id, exercise_id)
        self.log.info("exercise %s", exercise)
        if exercise is None:
            self.log.error("No exercise found")
            _forbidden("No exercise found")
        self.log.info("remove file url")
        await self.s3.remove_file_url(self.s3.bucket, exercise.get_key_media_url_path_old())
        self.log.info("remove exercise id")
        await self.repo.remove_exercise_id(exercise_id)
        return exercise
