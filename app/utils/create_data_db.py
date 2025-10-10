import random
from typing import List
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import settings
from db.models import UserModel, ExerciseModel, WorkoutModel, WorkoutExerciseModel
from services.auth_service import AuthServ


async def create_db_data(count_user: int = 5, count_exercise_for_user: int = 10, count_workout_for_user: int = 3):
    fake = Faker()
    engine = create_async_engine(settings.POSTGRES_URL, future=True)
    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with SessionLocal() as session:
        async with session.begin():
            stmt = select(UserModel).limit(1)
            result = await session.execute(stmt)
            user_in_db = result.scalars().first()
            if user_in_db is not None:
                return {"response": "Database already has a user."}
            list_users: List[UserModel] = []
            for user_number in range(count_user):
                user = UserModel(
                    email=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    birth_data=fake.date_of_birth(),
                    is_active=True,
                    is_confirmed=True,
                    is_admin=(user_number == 0),
                )
                user.password_hash = await AuthServ.hash_password(user.email)
                session.add(user)
                await session.flush()
                list_users.append(user)

            for user in list_users:
                list_exercise: List[ExerciseModel] = []

                for exercise_number in range(count_exercise_for_user):
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
                            media_url=fake.url(),
                            repetitions=random.randrange(10, 31, 10),
                            count_sets=random.randint(3, 8),
                            rest_sec=random.randint(30, 180),
                        )
                    session.add(exercise)
                    await session.flush()
                    list_exercise.append(exercise)
                for workout_number in range(count_workout_for_user):
                    workout = WorkoutModel(
                        title=f"Workout title user {user.email} {workout_number}",
                        description=f"Workout description {workout_number}",
                        user_id=user.id
                    )
                    session.add(workout)
                    await session.flush()
                    random_count_workout_exercise = random.randint(6, 8)
                    for k in range(random_count_workout_exercise):
                        exercise_random = random.choice(list_exercise)
                        workout_exercise = WorkoutExerciseModel(
                            workout_id=workout.id,
                            exercise_id=exercise_random.id,
                            position=k
                        )
                        session.add(workout_exercise)
                    await session.flush()
