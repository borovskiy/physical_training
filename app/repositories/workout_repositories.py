from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from db.models import WorkoutModel, WorkoutExerciseModel, GroupMemberModel
from repositories.base_repositoriey import BaseRepo


class WorkoutRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.workout_model = WorkoutModel
        self.model_group_member = GroupMemberModel

    async def add_workout(self, data: dict, user_id: int) -> WorkoutModel:
        obj = self.workout_model(**data)
        obj.user_id = user_id  # создаём объект
        self.session.add(obj)  # добавляем в сессию
        await self.session.commit()  # фиксируем
        await self.session.refresh(obj)  # подтягиваем id и т.п. сгенерированные БД
        return obj

    async def get_workout(self, workout_id: int) -> WorkoutModel:
        stmt = select(self.workout_model).where(self.workout_model.id == workout_id).options(
            selectinload(self.workout_model.workout_exercise)
            .selectinload(WorkoutExerciseModel.exercises)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_workout_with_user(self, workout_id: int, user_id: int) -> WorkoutModel:
        stmt = select(self.workout_model).where(
            and_(
                self.workout_model.id == workout_id,
                self.workout_model.user_id == user_id
            )).options(
            joinedload(self.workout_model.group_members)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all_workouts(self, user_id: int, limit: int, start: int):
        subquery = (
            select(self.model_group_member.workout_id)
            .where(
                self.model_group_member.user_id == user_id,
                self.model_group_member.workout_id.is_not(None)
            )
            .subquery()
        )

        stmt = (
            select(self.workout_model)
            .where(
                or_(
                    self.workout_model.user_id == user_id,
                    self.workout_model.id.in_(select(subquery.c.workout_id))
                )
            )
            .order_by(self.workout_model.created_at.asc())
            .offset(limit * start)
            .limit(limit)
        )
        workouts = (await self.session.execute(stmt)).scalars().all()

        stmt_count = select(func.count()).select_from(
            select(self.workout_model.id)
            .where(
                or_(
                    self.workout_model.user_id == user_id,
                    self.workout_model.id.in_(select(subquery.c.workout_id))
                )
            )
            .subquery()
        )
        total = (await self.session.execute(stmt_count)).scalar_one()
        return workouts, total

    async def remove_workout_id(self, workout: WorkoutModel) -> WorkoutModel | None:
        await self.session.delete(workout)
        await self.session.commit()
