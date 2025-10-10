import pytest
from db.models import WorkoutModel, UserModel
from repositories.workout_repositories import WorkoutRepository


@pytest.mark.asyncio
class TestWorkoutRepository:
    async def test_add_and_get_workout(self, session):
        repo = WorkoutRepository(session)

        user = UserModel(email="workout@example.com", password_hash="123")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        workout_data = {"title": "Morning Routine", "description": "Warm up"}
        workout = await repo.add_workout(workout_data, [], user.id)

        assert workout.id is not None
        assert workout.user_id == user.id

        found = await repo.get_workout_for_user(workout.id, user.id)
        assert found.title == "Morning Routine"

    async def test_get_workout_count(self, session):
        repo = WorkoutRepository(session)

        user = UserModel(email="count@example.com", password_hash="123")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        w1 = WorkoutModel(title="W1", user_id=user.id)
        w2 = WorkoutModel(title="W2", user_id=user.id)
        session.add_all([w1, w2])
        await session.commit()

        count = await repo.get_workout_count(user.id)
        assert count == 2

    async def test_remove_workout(self, session):
        repo = WorkoutRepository(session)

        user = UserModel(email="delete_workout@example.com", password_hash="123")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        workout = WorkoutModel(title="To Delete", user_id=user.id)
        session.add(workout)
        await session.commit()
        await session.refresh(workout)

        result = await repo.remove_workout_id(workout)
        assert result is True
