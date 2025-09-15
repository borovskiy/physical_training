from typing import List, Any, Coroutine, Sequence

from fastapi import HTTPException
from sqlalchemy import update, select, delete, Row, RowMapping, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.s3_cloud_connector import S3CloudConnector
from db.models import Exercise
from db.schemas.workout import WorkoutExerciseCreateSchema
from repositories.base_repositoriey import BaseRepo


class ExerciseRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Exercise

    async def add_exercise(self, data: dict, user_id: int) -> Exercise:
        obj = self.model(**data)
        obj.owner_id = user_id
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update_link_exercise(self, exercise_id: int, exercise_link: str):
        stmt = update(Exercise).where(Exercise.id == exercise_id).values(media_url=exercise_link)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.session.get(Exercise, exercise_id)

    async def get_all_exercise(self, user_id: int, limit: int, start: int) -> tuple[Sequence[Exercise], Any]:
        stmt_exercise = (
            select(self.model)
            .where(self.model.owner_id == user_id)
            .order_by(self.model.created_at.asc())
            .offset(limit * start)
            .limit(limit)
        )
        res_exercise = await self.session.execute(stmt_exercise)
        exercise = res_exercise.scalars().all()
        stmt_count_exercise = select(func.count()).select_from(
            select(self.model.id).where(self.model.owner_id == user_id).subquery()
        )
        total = (await self.session.execute(stmt_count_exercise)).scalar_one()
        return exercise, total

    async def get_by_id(self, user_id: int, exercise_id: int | str) -> Exercise | None:
        stmt_exercise = (
            select(self.model)
            .where(
                and_(
                    Exercise.id == exercise_id,
                    Exercise.owner_id == user_id
                )
            )

        )
        res = await self.session.execute(stmt_exercise)
        return res.scalars().first()

    async def update_exercise(self, data: dict, user_id: int, exercise_id: int) -> Exercise:
        stmt = (update(Exercise).where(
            and_(
                Exercise.id == exercise_id,
                Exercise.owner_id == user_id
            )
        ).values(**data)
                .returning(Exercise))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_count_self_exercise(self, user_id: int, list_id_exercise: List[WorkoutExerciseCreateSchema]) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)  # или Workout
            .where(
                self.model.owner_id == user_id,  # для Workout -> Workout.user_id
                self.model.id.in_([i.exercise_id for i in list_id_exercise]),
            )
        )
        cnt = await self.session.scalar(stmt)
        return cnt


    async def remove_exercise_id(self, id_exercise: int) -> Exercise | None:
        stmt = delete(self.model).where(self.model.id == id_exercise)
        result = await self.session.execute(stmt)
        return result.scalars().first()
