from enum import nonmember
from math import ceil
from typing import Sequence

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_only

from core.s3_cloud_connector import S3CloudConnector
from db.models import User, Exercise
from db.schemas.exercise import CreateExerciseSchema, ExercisePage, PageMeta, UpdateExerciseSchema
from repositories.exercise_repositories import ExerciseRepository
from services.auth_service import _forbidden


class ExerciseServices:
    def __init__(self, session: AsyncSession):
        self.repo = ExerciseRepository(session)
        self.s3 = S3CloudConnector()

    async def get_exercises(self, current_user: User, limit: int, start: int) -> ExercisePage:
        exercise, total = await self.repo.get_all_exercise(current_user.id, limit, start)
        pages = ceil(total / limit) if limit else 1
        return ExercisePage(
            exercise=exercise,
            meta=PageMeta(total=total, limit=limit, pages=pages),
        )

    async def get_exercise(self, current_user: User, exercise_id: int) -> Exercise:
        exercise = await self.repo.get_by_id(current_user.id, exercise_id)
        return exercise

    async def add_exercise(self, current_user: User, payload: CreateExerciseSchema, file: UploadFile) -> Exercise:
        new_exercise = await self.repo.add_exercise(payload.model_dump(), current_user.id)
        name_key_file = f"{current_user.email}/exercise_file/{new_exercise.id}/{file.filename}"
        link_exercise = await self.s3.upload_upload_file(self.s3.bucket, name_key_file, file, True)
        new_exercise = await self.repo.update_link_exercise(new_exercise.id, link_exercise)
        return new_exercise

    async def update_exercise(self, exercise_id: int, schema: UpdateExerciseSchema, current_user: User) -> Exercise:
        result = await self.repo.update_exercise(schema.model_dump(), current_user.id, exercise_id)
        return result

    async def update_file_exercise(self, current_user: User, exercise_id: int, file: UploadFile) -> Exercise | None:
        exercise = await self.repo.get_by_id(current_user.id, exercise_id)
        if exercise is not None:
            link_for_remove = exercise.get_key_media_url_path_old()
            name_key_file = exercise.get_media_url_path(file)
            link_exercise = await self.s3.upload_upload_file(self.s3.bucket, name_key_file, file, True)
            new_exercise = await self.repo.update_link_exercise(exercise_id, link_exercise)
            if link_for_remove != name_key_file and link_for_remove is not None:
                await self.s3.remove_file_url(self.s3.bucket, link_for_remove)
            return new_exercise
        else:
            return None

    async def remove_exercise(self, exercise_id: int, user: User):
        get_exercise = await self.repo.get_by_id(user.id, exercise_id)
        if get_exercise is None:
            _forbidden("No exercise found")
        result = await self.repo.remove_exercise_id(exercise_id)
        return result