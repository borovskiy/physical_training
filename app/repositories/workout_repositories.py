import logging
from typing import List

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from db.models import WorkoutModel, GroupMemberModel, ExerciseModel, GroupModel, UserModel
from db.models.workout_model import WorkoutExerciseModel
from db.schemas.workout_schema import WorkoutExerciseCreateSchema
from repositories.base_repositoriey import BaseRepo

logger = logging.getLogger(__name__)


class WorkoutRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.workout_model = WorkoutModel
        self.model_group_member = GroupMemberModel
        self.model_group = GroupModel
        self.model_exercise = ExerciseModel
        self.model_user = UserModel
        self.model_workout_exercise = WorkoutExerciseModel

    async def add_workout(self, data: dict, exercises_schema: List[WorkoutExerciseCreateSchema],
                          user_id: int) -> WorkoutModel:
        logger.info("Try create workout %s", data)
        workout_obj = self.workout_model(**data)
        workout_obj.user_id = user_id
        for schema in exercises_schema:
            exercise = self.model_workout_exercise(**schema.model_dump())
            workout_obj.exercises.append(exercise)
        logger.info("New workout %s", workout_obj)
        self.session.add(workout_obj)
        await self.session.commit()
        await self.session.refresh(workout_obj)
        return workout_obj

    async def update_workout(self, workout_id: int, current_user_id: int,
                             exercises_schema: List[WorkoutExerciseCreateSchema]) -> WorkoutModel:
        logger.info("Try update workout %s", workout_id)
        workout_obj = await self.get_workout_with_user(workout_id, current_user_id)
        logger.info("Try workout %s", workout_obj)
        workout_obj.exercises.clear()
        for schema in exercises_schema:
            exercise = self.model_workout_exercise(**schema.model_dump())
            workout_obj.exercises.append(exercise)
        self.session.add(workout_obj)
        logger.info("New workout %s", workout_obj)
        await self.session.commit()
        await self.session.refresh(workout_obj)
        return workout_obj

    async def get_workout_count(self, user_id: int) -> int:
        logger.info("Try workouts count")
        stmt = select(func.count()).select_from(
            select(self.workout_model).where(self.workout_model.user_id == user_id).subquery())
        return (await self.session.execute(stmt)).scalar_one()

    async def get_workout_with_user(self, workout_id: int, user_id: int) -> WorkoutModel:
        logger.info("Try workout with user")
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
        logger.info("Try get limit workouts")
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
        logger.info("Try get count workouts")
        total = await self.get_workout_count(user_id)
        return workouts, total

    async def remove_workout_id(self, workout: WorkoutModel) -> WorkoutModel | None:
        logger.info("Try remove workout by id %s", workout.id)
        await self.session.delete(workout)
        await self.session.commit()
