import pytest
from db.models import ExerciseModel, UserModel
from repositories.exercise_repositories import ExerciseRepository


@pytest.mark.asyncio
class TestExerciseRepository:
    async def test_add_and_get_exercise(self, session):
        repo = ExerciseRepository(session)

        user = UserModel(email="exercise@example.com", password_hash="123")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        exercise = ExerciseModel(title="Push-ups", user_id=user.id)
        session.add(exercise)
        await session.commit()
        await session.refresh(exercise)

        found = await repo.get_by_id(user.id, exercise.id)
        assert found.id == exercise.id
        assert found.title == "Push-ups"

    async def test_update_exercise(self, session):
        repo = ExerciseRepository(session)

        user = UserModel(email="update_exercise@example.com", password_hash="123")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        exercise = ExerciseModel(title="Squats", user_id=user.id)
        session.add(exercise)
        await session.commit()
        await session.refresh(exercise)

        updated = await repo.update_exercise({"title": "Deep Squats"}, user.id, exercise.id)
        assert updated.title == "Deep Squats"

    async def test_get_all_exercises_and_count(self, session):
        repo = ExerciseRepository(session)

        user = UserModel(email="count_exercise@example.com", password_hash="123")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        ex1 = ExerciseModel(title="E1", user_id=user.id)
        ex2 = ExerciseModel(title="E2", user_id=user.id)
        session.add_all([ex1, ex2])
        await session.commit()

        items, total = await repo.get_all_exercise_user(user.id, limit=10, start=0)
        assert total == 2
        assert len(items) == 2

    async def test_remove_exercise(self, session):
        repo = ExerciseRepository(session)

        user = UserModel(email="remove_exercise@example.com", password_hash="123")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        exercise = ExerciseModel(title="Burpees", user_id=user.id)
        session.add(exercise)
        await session.commit()
        await session.refresh(exercise)

        await repo.remove_exercise_id(exercise.id)
        result = await repo.get_by_id(user.id, exercise.id)
        assert result is None
