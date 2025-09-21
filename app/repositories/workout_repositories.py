from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from db.models import WorkoutModel, GroupMemberModel, ExerciseModel, GroupModel, UserModel
from db.models.workout_model import WorkoutExerciseModel
from repositories.base_repositoriey import BaseRepo


class WorkoutRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.workout_model = WorkoutModel
        self.model_group_member = GroupMemberModel
        self.model_group = GroupModel
        self.model_exercise = ExerciseModel
        self.model_user = UserModel

        self.model_workout_exercise = WorkoutExerciseModel

    async def add_workout(self, data: dict, user_id: int) -> WorkoutModel:
        obj = self.workout_model(**data)
        obj.user_id = user_id
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_workout_count(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(select(self.workout_model).where(self.workout_model.user_id == user_id).subquery())
        return (await self.session.execute(stmt)).scalar_one()

    async def get_workout_with_user(self, workout_id: int, user_id: int) -> WorkoutModel:
        stmt = (
            select(self.workout_model)
            .options(
                selectinload(self.workout_model.groups).selectinload(self.model_group.members),
                selectinload(self.workout_model.workout_exercises).selectinload(self.model_workout_exercise.exercise),
            )
            .where(
                self.workout_model.id == workout_id,
                or_(
                    self.workout_model.user_id == user_id,
                    self.workout_model.groups.any(
                        self.model_group.members.any(self.model_group_member.user_id == user_id)
                    ),
                )
            )
        )
        return await self.session.scalar(stmt)

    async def get_all_workouts(self, user_id: int, limit: int, start: int):
        stmt = (
            select(self.workout_model)
            .options(
                selectinload(self.workout_model.groups).selectinload(self.model_group.members))
            .where(
                or_(
                    self.workout_model.user_id == user_id,
                    self.workout_model.groups.any(
                        self.model_group.members.any(self.model_group_member.user_id == user_id))
                )
            )
            .order_by(self.workout_model.created_at.asc())
            .offset(limit * start)
            .limit(limit)
        )
        workouts = (await self.session.execute(stmt)).scalars().all()

        stmt_count = select(func.count()).select_from(
            select(self.workout_model).options(
                joinedload(self.workout_model.groups).joinedload(self.model_group.members))
            .where(
                or_(
                    self.workout_model.user_id == user_id,
                    self.workout_model.groups.any(
                        self.model_group.members.any(self.model_group_member.user_id == user_id))
                )
            )
            .subquery()
        )
        total = (await self.session.execute(stmt_count)).scalar_one()
        return workouts, total

    async def remove_workout_id(self, workout: WorkoutModel) -> WorkoutModel | None:
        await self.session.delete(workout)
        await self.session.commit()
