from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Workout, WorkoutExercise
from db.schemas.paginate import PaginationGet
from repositories.base_repositoriey import BaseRepo


class WorkoutRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Workout

    async def add_workout(self, data: dict, user_id: int) -> Workout:
        obj = self.model(**data)
        obj.user_id = user_id  # создаём объект
        self.session.add(obj)  # добавляем в сессию
        await self.session.commit()  # фиксируем
        await self.session.refresh(obj)  # подтягиваем id и т.п. сгенерированные БД
        return obj

    async def get_workout(self, workout_id: int) -> Workout:
        stmt = select(self.model).where(Workout.id == workout_id).options(
            # 1) подгружаем элементы воркаута
            selectinload(Workout.items)
            # 2) и для каждого элемента подгружаем упражнение
            .selectinload(WorkoutExercise.exercise)
        )
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


        stmt = select(self.model).where(Workout.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()