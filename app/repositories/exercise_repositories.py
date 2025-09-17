from typing import List, Any, Sequence

from sqlalchemy import update, select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ExerciseModel
from db.schemas.workout import WorkoutExerciseCreateSchema
from repositories.base_repositoriey import BaseRepo


class ExerciseRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = ExerciseModel

    async def add_exercise(self, data: dict, user_id: int) -> ExerciseModel:
        obj = self.model(**data)
        obj.user_id = user_id
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update_link_exercise(self, exercise_id: int, exercise_link: str):
        stmt = update(self.model).where(self.model.id == exercise_id).values(media_url=exercise_link)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.session.get(ExerciseModel, exercise_id)

    async def get_all_exercise(self, user_id: int, limit: int, start: int) -> tuple[Sequence[ExerciseModel], Any]:
        stmt_exercise = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.asc())
            .offset(limit * start)
            .limit(limit)
        )
        res_exercise = await self.session.execute(stmt_exercise)
        exercise = res_exercise.scalars().all()
        stmt_count_exercise = select(func.count()).select_from(
            select(self.model.id).where(self.model.user_id == user_id).subquery()
        )
        total = (await self.session.execute(stmt_count_exercise)).scalar_one()
        return exercise, total

    async def get_by_id(self, user_id: int, exercise_id: int | str) -> ExerciseModel | None:
        stmt_exercise = (
            select(self.model)
            .where(
                and_(
                    self.model.id == exercise_id,
                    self.model.user_id == user_id
                )
            )

        )
        res = await self.session.execute(stmt_exercise)
        return res.scalars().first()

    async def update_exercise(self, data: dict, user_id: int, exercise_id: int) -> ExerciseModel:
        stmt = (update(self.model).where(
            and_(
                self.model.id == exercise_id,
                self.model.user_id == user_id
            )
        ).values(**data).returning(self.model)
                )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_count_self_exercise(self, user_id: int, list_id_exercise: List[WorkoutExerciseCreateSchema]) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)  # или Workout
            .where(
                self.model.user_id == user_id,  # для Workout -> Workout.user_id
                self.model.id.in_([i.exercise_id for i in list_id_exercise]),
            )
        )
        cnt = await self.session.scalar(stmt)
        return cnt

    async def remove_exercise_id(self, exercise: ExerciseModel) -> ExerciseModel | None:
        await self.session.delete(exercise)
        await self.session.commit()
