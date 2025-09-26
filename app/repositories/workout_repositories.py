from typing import List

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.db.models import WorkoutModel, GroupMemberModel, ExerciseModel, GroupModel, UserModel
from app.db.models.workout_model import WorkoutExerciseModel
from app.db.schemas.workout_schema import WorkoutExerciseCreateSchema, ExerciseCreateSchema
from app.repositories.base_repositoriey import BaseRepo


class WorkoutRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.workout_model = WorkoutModel
        self.model_group_member = GroupMemberModel
        self.model_group = GroupModel
        self.model_exercise = ExerciseModel
        self.model_user = UserModel
        self.model_workout_exercise = WorkoutExerciseModel

    async def add_workout(self, data: dict, exercises_schema: List[ExerciseCreateSchema], user_id: int) -> WorkoutModel:
        self.log.info("add_workout data %s", data)
        workout_obj = self.workout_model(**data)
        workout_obj.user_id = user_id
        for schema in exercises_schema:
            exercise = self.model_workout_exercise(**schema.model_dump())
            workout_obj.workout_exercises.append(exercise)
        self.log.info("New workout %s", workout_obj)
        self.session.add(workout_obj)
        await self.session.commit()
        await self.session.refresh(workout_obj)
        return workout_obj

    async def update_workout(self, workout_id: int, current_user_id: int,
                             workout_schema: WorkoutExerciseCreateSchema) -> WorkoutModel:
        self.log.info("update_workout id %s, user id %s, exercises_schema %s", workout_id, current_user_id,
                      workout_schema)
        workout_obj = await self.get_workout_with_user(workout_id, current_user_id)
        self.log.info("Workout %s", workout_obj)
        workout_obj.title = workout_schema.workout.title
        workout_obj.description = workout_schema.workout.description
        workout_obj.workout_exercises.clear()
        await self.session.flush()
        for schema in workout_schema.exercises:
            exercise = self.model_workout_exercise(**schema.model_dump())
            workout_obj.workout_exercises.append(exercise)
        self.session.add(workout_obj)
        self.log.info("New workout %s", workout_obj)
        await self.session.commit()
        await self.session.refresh(workout_obj)
        return workout_obj

    async def get_workout_count(self, user_id: int) -> int:
        self.log.info("get_workout_count user id %s", user_id)
        stmt = select(func.count()).select_from(
            select(self.workout_model).where(self.workout_model.user_id == user_id).subquery())
        return (await self.session.execute(stmt)).scalar_one()

    async def get_workout_with_user(self, workout_id: int, user_id: int) -> WorkoutModel:
        self.log.info("get_workout_with_user workout id %s, user id %s", workout_id, user_id)
        stmt = (
            select(self.workout_model)
            .options(
                selectinload(self.workout_model.groups).selectinload(self.model_group.members),
                selectinload(self.workout_model.workout_exercises).selectinload(self.model_workout_exercise.exercise),
                selectinload(self.workout_model.exercises),
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
        self.log.info("get_all_workouts user id %s limit %s start %s", user_id, limit, start)
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
        self.log.info("Try get count workouts")
        total = await self.get_workout_count(user_id)
        return workouts, total

    async def remove_workout_id(self, workout: WorkoutModel) -> WorkoutModel | None:
        self.log.info("remove_workout_id id %s", workout.id)
        await self.session.delete(workout)
        await self.session.commit()
