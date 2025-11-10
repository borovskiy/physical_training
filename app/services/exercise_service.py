from math import ceil

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.s3_cloud_connector import S3CloudConnector
from db.models import ExerciseModel
from db.schemas.exercise_schema import CreateExerciseSchema, ExercisePage, PageMeta, UpdateExerciseSchema
from repositories.exercise_repositories import ExerciseRepository
from repositories.user_repository import UserRepository
from services.base_services import BaseServices
from utils.context import get_current_user


class ExerciseServices(BaseServices):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.repo = ExerciseRepository(session)
        self.repo_user = UserRepository(session)
        self.s3 = S3CloudConnector()

    async def get_exercises(self, limit: int, start: int, user_id: int) -> ExercisePage:
        self.log.info("Try get exercises")
        exercises, total = await self.repo.get_all_exercise_user(
            BaseServices.check_permission(get_current_user(), user_id), limit, start)
        self.log.info("exercises %s", exercises)
        self.log.info("total %s", total)
        pages = ceil(total / limit) if limit else 1
        return ExercisePage(
            meta=PageMeta(total=total, limit=limit, pages=pages),
            exercises=exercises,
        )

    async def get_exercise(self, exercise_id: int) -> ExerciseModel:
        self.log.info("Try get exercise")
        return await self.repo.get_by_id(get_current_user().id, exercise_id, get_current_user().is_admin)

    async def create_exercise(self, payload: CreateExerciseSchema, file: UploadFile,
                              user_id: int | None = None) -> ExerciseModel:
        self.log.info("add_exercise")
        user = await self.repo_user.find_user_id(BaseServices.check_permission(get_current_user(), user_id), False)
        user_id = user_id if user_id is not None else user.id
        user.check_reached_limit_exercises(await self.repo.get_count_exercise_user(user_id))
        payload._user_id = user_id
        new_exercise = await self.repo.create_one_obj_model(payload.model_dump())
        self.log.info("New exercise %s", new_exercise)
        self.log.info("Try upload file")
        link_exercise = await self.s3.upload_upload_file(self.s3.bucket, new_exercise.get_media_url_path(file), file,
                                                         True)
        self.log.info("link exercise %s", link_exercise)
        new_exercise = await self.repo.update_link_exercise(new_exercise.id, link_exercise)
        self.log.info("New exercise %s", new_exercise)
        return new_exercise

    async def update_exercise(self, exercise_id: int, schema: CreateExerciseSchema) -> ExerciseModel:
        self.log.info("update exercise id %s", exercise_id)
        exercise = await self.repo.get_by_id(get_current_user().id, exercise_id, get_current_user().is_admin)
        self.log.info("exercise %s", exercise)
        schema._user_id = exercise.user_id
        new_exercise = await self.repo.update_exercise(schema.model_dump(), exercise.user_id, exercise_id)
        self.log.info("New exercise %s", new_exercise)
        return new_exercise

    async def update_file_exercise(self, exercise_id: int, file: UploadFile) -> ExerciseModel | None:
        self.log.info("update file exercise id %s", exercise_id)
        exercise = await self.repo.get_by_id(get_current_user().id, exercise_id, get_current_user().is_admin)
        self.log.info("exercise %s", exercise)
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

    async def remove_exercise_from_all_workout(self, exercise_id: int) -> ExerciseModel:
        self.log.info("remove exercise from all workout id %s", exercise_id)
        exercise = await self.repo.get_by_id(get_current_user().id, exercise_id, get_current_user().is_admin)
        self.log.info("exercise %s", exercise)
        self.log.info("remove file url")
        await self.s3.remove_file_url(self.s3.bucket, exercise.get_key_media_url_path_old())
        self.log.info("remove exercise id")
        await self.repo.remove_exercise_id(exercise_id)
        return exercise
