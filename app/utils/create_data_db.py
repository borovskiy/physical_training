import random
from typing import List

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import settings
from db.models import UserModel, ExerciseModel, WorkoutModel, WorkoutExerciseModel
from faker import Faker

from services.auth_service import hash_password


async def create_db_data(count_user: int = 5, count_exercise_for_user: int = 40, count_workout_for_user: int = 5):
    fake = Faker()

    # Убедитесь, что settings.DB_URL использует async-драйвер:
    # например: postgresql+asyncpg://user:pass@host:5432/dbname
    engine = create_async_engine(settings.DB_URL, future=True)
    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with SessionLocal() as session:
        # Одна транзакция для всей операции (можно сделать и по пользователю, если нужно)
        async with session.begin():
            list_users: List[UserModel] = []

            # Создаём пользователей
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
                # хеш пароля — синхронная функция, вызываем заранее
                user.password_hash = await hash_password(user.email)

                session.add(user)
                # flush — чтобы user.id стал доступен без коммита
                await session.flush()
                list_users.append(user)

            # Для каждого пользователя создаём упражнения и тренировки
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
                    # flush чтобы получить exercise.id
                    await session.flush()
                    list_exercise.append(exercise)

                # Создаём тренировки и привязываем случайные упражнения
                for workout_number in range(count_workout_for_user):
                    workout = WorkoutModel(
                        title=f"Workout title user {user.email} {workout_number}",
                        description=f"Workout description {workout_number}",
                        user_id=user.id
                    )
                    session.add(workout)
                    await session.flush()  # чтобы workout.id стал доступен

                    random_count_workout_exercise = random.randint(6, 8)
                    for k in range(random_count_workout_exercise):
                        # выбрали упражнение — без лишней запятой!
                        exercise_random = random.choice(list_exercise)

                        workout_exercise = WorkoutExerciseModel(
                            workout_id=workout.id,
                            exercise_id=exercise_random.id,
                            position=k
                        )

                        session.add(workout_exercise)

                    # можно flush по окончании добавления упражнений в тренировку
                    await session.flush()

        # выход из session.begin() совершит commit, если не было исключений
