from typing import List, Any, Sequence

from sqlalchemy import update, select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ExerciseModel, WorkoutExerciseModel
from repositories.base_repositoriey import BaseRepo
from utils.raises import _forbidden, _not_found


class ExerciseRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = ExerciseModel
        self.model_workout_exercise = WorkoutExerciseModel

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

    async def get_all_exercise_user(self, user_id: int, limit: int, start: int) -> tuple[Sequence[ExerciseModel], Any]:
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

    async def get_count_exercise_user(self, user_id: int) -> int:
        stmt_count_exercise = select(func.count()).select_from(
            select(self.model.id).where(self.model.user_id == user_id).subquery()
        )
        return (await self.session.execute(stmt_count_exercise)).scalar_one()

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
        await self.session.commit()
        return result.scalar_one_or_none()

    async def find_count_self_exercise(self, user_id: int, list_id_exercise: List[int]) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)  # или Workout
            .where(
                self.model.user_id == user_id,  # для Workout -> Workout.user_id
                self.model.id.in_(list_id_exercise),
            )
        )
        cnt = await self.session.scalar(stmt)
        return cnt

    async def remove_exercise_id(self, exercise_id: int, start_index: int = 1) -> None:
        workouts_touched: set[int] = set()
        total_deleted = 0

        # ↓↓↓ ключевая правка ↓↓↓
        async with self.session.begin_nested():
            # 1) workout_ids
            stmt = select(self.model_workout_exercise.workout_id) \
                .where(self.model_workout_exercise.exercise_id == exercise_id) \
                .distinct()
            res = await self.session.execute(stmt)
            workout_ids = [row[0] for row in res.all()]

            if not workout_ids:
                raise _forbidden("Not Found workout for exercise Id")  # (логичнее 404, но оставляю как есть)

            for workout_id in workout_ids:
                # 2) ассоциации по порядку
                stmt = select(self.model_workout_exercise) \
                    .where(self.model_workout_exercise.workout_id == workout_id) \
                    .order_by(self.model_workout_exercise.position)
                res = await self.session.execute(stmt)
                assoc_list = res.scalars().all()
                if not assoc_list:
                    continue

                # 3) фильтрация
                remaining = [a for a in assoc_list if a.exercise_id != exercise_id]
                removed_count = len(assoc_list) - len(remaining)
                if removed_count == 0:
                    continue

                # 4) delete
                del_stmt = delete(self.model_workout_exercise).where(
                    (self.model_workout_exercise.workout_id == workout_id) &
                    (self.model_workout_exercise.exercise_id == exercise_id)
                )
                await self.session.execute(del_stmt)
                total_deleted += removed_count
                workouts_touched.add(workout_id)

                # 5) перенумерация (минимизируем UPDATE)
                for new_pos, assoc in enumerate(remaining, start=start_index):
                    if assoc.position != new_pos:
                        upd = update(self.model_workout_exercise) \
                            .where(self.model_workout_exercise.id == assoc.id) \
                            .values(position=new_pos)
                        await self.session.execute(upd)
