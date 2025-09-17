import random
from typing import List

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import settings
from db.models import UserModel, ExerciseModel, WorkoutModel, WorkoutExerciseModel
from faker import Faker

from services.auth_service import hash_password


async def create_db_data(count_user: int = 3, count_exercise_for_user: int = 40, count_workout_for_user: int = 5):
    fake = Faker()
    SessionLocal = async_sessionmaker(
        bind=create_async_engine(settings.DB_URL),
        expire_on_commit=False,
    )

    async with SessionLocal() as session:

        list_users = []
        for user_number in range(0, count_user):
            user = UserModel(
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                birth_data=fake.date_of_birth(),
                is_active=True,
                is_confirmed=True,
                is_admin=True if user_number == 0 else False,
            )
            user.password_hash = hash_password(user.email)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            list_users.append(user)

        for user in list_users:
            list_exercise: List[ExerciseModel] = []
            exercise = ExerciseModel()
            for exercise_number in range(0, count_exercise_for_user):
                if random.randint(0, 1) == 1:
                    exercise = ExerciseModel(
                        user_id=user.id,
                        title=f"Title exercise {exercise_number}",
                        type="strength",
                        description=f"Description exercise {exercise_number}",
                        media_url=fake.url() if random.randint(0, 1) else None,
                        time_work=random.randrange(30, 181, 10),
                        rest_sec=random.randint(30, 180),
                    )
                else:
                    exercise = ExerciseModel(
                        user_id=user.id,
                        title=f"Title exercise {exercise_number}",
                        type="strength",
                        description=f"Description exercise {exercise_number}",
                        media_url=fake.url() if random.randint(0, 1) else None,
                        repetitions=random.randrange(10, 31, 10),
                        count_sets=random.randint(3, 8),  # разумнее, чем 30..180
                        rest_sec=random.randint(30, 180),
                    )
                session.add(exercise)
                await session.commit()
                await session.refresh(exercise)
                list_exercise.append(exercise)
            for workout_number in range(0, count_workout_for_user):
                workout = WorkoutModel(
                    title=f"Workout title user {user.email} {workout_number}",
                    description=f"Workout description {workout_number}",
                    user_id=user.id
                )
                session.add(workout)
                await session.commit()
                await session.refresh(workout)
                random_count_workout_exercise = random.randint(6, 8)
                for k in range(0, random_count_workout_exercise):
                    exercise_random = random.choice(list_exercise),
                    workout_exercise = WorkoutExerciseModel(
                        workout_id=workout.id,
                        exercise_id=exercise_random[0].id,
                        position=k
                    )

                    session.add(workout_exercise)
                    await session.commit()
                    await session.refresh(workout_exercise)
