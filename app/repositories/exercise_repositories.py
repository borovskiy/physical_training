from typing import List, Any, Sequence

from sqlalchemy import update, select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ExerciseModel, WorkoutExerciseModel
from repositories.base_repositoriey import BaseRepo


class ExerciseRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = ExerciseModel
        self.model_workout_exercise = WorkoutExerciseModel

    async def get_all_exercise_user(self, user_id: int, limit: int, start: int) -> tuple[Sequence[ExerciseModel], Any]:
        self.log.info("get_all_exercise_user %s limit %s start %s", user_id, limit, start)
        stmt_exercise = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.asc())
            .offset(limit * start)
            .limit(limit)
        )
        res_exercise = await self.session.execute(stmt_exercise)
        exercises = res_exercise.scalars().all()
        self.log.info(f"exercises {exercises}")
        total = await self.get_count_exercise_user(user_id)
        self.log.info(f"count all exercises {total}")
        return exercises, total

    async def get_by_id(self, user_id: int, exercise_id: int | str) -> ExerciseModel | None:
        self.log.info("get_by_id user_id %s exercise_id %s", user_id, exercise_id)
        stmt_exercise = (
            select(self.model)
            .where(
                and_(
                    self.model.id == exercise_id,
                    self.model.user_id == user_id
                )
            )

        )
        return await self.execute_session_get_first(stmt_exercise)

    async def get_count_exercise_user(self, user_id: int) -> int:
        self.log.info("get_count_exercise_user %s", user_id)
        stmt_count_exercise = select(func.count()).select_from(
            select(self.model.id).where(self.model.user_id == user_id).subquery()
        )
        return await self.execute_session_get_one(stmt_count_exercise)

    async def update_exercise(self, data: dict, user_id: int, exercise_id: int) -> ExerciseModel:
        self.log.info("update_exercise by data %s, user_id %s, exercise_id %s", data, user_id, exercise_id)
        stmt = (
            update(self.model).where(
                and_(
                    self.model.id == exercise_id,
                    self.model.user_id == user_id
                )
            ).values(**data).returning(self.model)
        )
        await self.execute_session_and_commit(stmt)
        return await self.get_by_id(user_id, exercise_id)

    async def find_count_self_exercise(self, user_id: int, list_id_exercise: List[int]) -> int:
        self.log.info("find_count_self_exercise list id exercise %s, user id %s", list_id_exercise, user_id)
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.id.in_(list_id_exercise),
            )
        )
        return await self.execute_session_get_one(stmt)

    async def remove_exercise_id(self, exercise_id: int, start_index: int = 1) -> None:
        self.log.info("remove_exercise_id %s", exercise_id)
        workouts_touched: set[int] = set()
        total_deleted = 0

        async with self.session.begin_nested():
            stmt = select(self.model_workout_exercise.workout_id) \
                .where(self.model_workout_exercise.exercise_id == exercise_id) \
                .distinct()
            res = await self.session.execute(stmt)
            workout_ids = [row[0] for row in res.all()]

            if not workout_ids:
                self.log.info("Not Found workout for exercise Id")
                del_stmt = delete(self.model).where(self.model.id == exercise_id)
                await self.session.execute(del_stmt)
                return await self.session.commit()

            for workout_id in workout_ids:
                self.log.info("Workout id %s", workout_id)
                stmt = select(self.model_workout_exercise) \
                    .where(self.model_workout_exercise.workout_id == workout_id) \
                    .order_by(self.model_workout_exercise.position)
                res = await self.session.execute(stmt)
                assoc_list = res.scalars().all()
                if not assoc_list:
                    continue

                remaining = [a for a in assoc_list if a.exercise_id != exercise_id]
                self.log.info("remaining list %s", remaining)
                removed_count = len(assoc_list) - len(remaining)
                self.log.info("removed count %s", removed_count)
                if removed_count == 0:
                    continue

                del_stmt = delete(self.model_workout_exercise).where(
                    (self.model_workout_exercise.workout_id == workout_id) &
                    (self.model_workout_exercise.exercise_id == exercise_id)
                )
                await self.session.execute(del_stmt)
                total_deleted += removed_count
                workouts_touched.add(workout_id)
                self.log.info("recalculate ordinal numbers")
                for new_pos, assoc in enumerate(remaining, start=start_index):
                    if assoc.position != new_pos:
                        upd = update(self.model_workout_exercise) \
                            .where(self.model_workout_exercise.id == assoc.id) \
                            .values(position=new_pos)
                        await self.session.execute(upd)
            del_exercise = delete(self.model).where(self.model.id == exercise_id)
            await self.session.execute(del_exercise)
        await self.session.commit()
        return None

    async def update_link_exercise(self, exercise_id: int, exercise_link: str):
        self.log.info("update_link_exercise id %s, link %s", exercise_id, exercise_link)
        stmt = update(self.model).where(self.model.id == exercise_id).values(media_url=exercise_link)
        await self.execute_session_and_commit(stmt)
        return await self.session.get(self.model, exercise_id)
