from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import WorkoutExerciseModel
from db.schemas.workout import WorkoutExerciseCreateSchema
from repositories.base_repositoriey import BaseRepo


class WorkoutExerciseRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = WorkoutExerciseModel

    async def add_workout_exercise(self, exercises_schema: List[WorkoutExerciseCreateSchema], workout_id: int,
                                   user_id: int) -> WorkoutExerciseModel:
        for schema in exercises_schema:
            obj = self.model(**schema.model_dump())
            obj.workout_id = workout_id
            obj.user_id = user_id  # создаём объект
            self.session.add(obj)  # добавляем в сессию
        await self.session.commit()  # фиксируем
        return obj


