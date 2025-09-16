from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import WorkoutModel, WorkoutExerciseModel
from repositories.base_repositoriey import BaseRepo


class WorkoutRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = WorkoutModel

    async def add_workout(self, data: dict, user_id: int) -> WorkoutModel:
        obj = self.model(**data)
        obj.user_id = user_id  # создаём объект
        self.session.add(obj)  # добавляем в сессию
        await self.session.commit()  # фиксируем
        await self.session.refresh(obj)  # подтягиваем id и т.п. сгенерированные БД
        return obj

    async def get_workout(self, workout_id: int) -> WorkoutModel:
        stmt = select(self.model).where(self.model.id == workout_id).options(
            selectinload(self.model.items)
            .selectinload(WorkoutExerciseModel.exercise)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_workout_with_user(self, workout_id: int, user_id: int) -> WorkoutModel:
        stmt = select(self.model).where(
            and_(
                self.model.id == workout_id,
                self.model.user_id == user_id
            ))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all_workouts(self, user_id: int, limit: int, start: int):
        stmt_workouts = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.asc())
            .offset(limit * start)
            .limit(limit)
        )
        res_workouts = await self.session.execute(stmt_workouts)
        workouts = res_workouts.scalars().all()
        stmt_count_workouts = select(func.count()).select_from(
            select(self.model.id).where(self.model.user_id == user_id).subquery()
        )
        total = (await self.session.execute(stmt_count_workouts)).scalar_one()
        return workouts, total

    async def remove_workout_id(self, workout: WorkoutModel) -> WorkoutModel | None:
        await self.session.delete(workout)
        await self.session.commit()
