import pytest
from datetime import datetime
from fastapi import UploadFile
from io import BytesIO

from db.models import UserModel, ExerciseModel
from db.models.user_model import PlanLimits
from db.schemas.user_schema import UserAdminGetModelSchema
from repositories.user_repository import UserRepository
from repositories.exercise_repositories import ExerciseRepository
from db.schemas.exercise_schema import CreateExerciseSchema
from core.s3_cloud_connector import S3CloudConnector
from services.exercise_service import ExerciseServices
from utils.context import set_current_user

import pytest
from db.models import UserModel
from repositories.user_repository import UserRepository
from utils.context import set_current_user
import pytest
from fastapi import HTTPException
from db.schemas.exercise_schema import parse_create_exercise_form


@pytest.fixture
async def user(session):
    repo = UserRepository(session)
    user1 = UserModel(
        email="user1@example.com",
        password_hash="hashed_pwd_1",
        first_name="Alice",
        last_name="Smith",
        is_admin=False,
        is_active=True,
        is_confirmed=True,
    )
    user2 = UserModel(
        email="user2@example.com",
        password_hash="hashed_pwd_2",
        first_name="Bob",
        last_name="Brown",
        is_admin=False,
        is_active=True,
        is_confirmed=True,
    )
    admin = UserModel(
        email="admin@example.com",
        password_hash="hashed_pwd_3",
        first_name="Root",
        last_name="Admin",
        is_admin=True,
        is_active=True,
        is_confirmed=True,
    )

    session.add_all([user1, user2, admin])
    await session.commit()

    await session.refresh(user1)
    await session.refresh(user2)
    await session.refresh(admin)

    return {
        "user1": user1,
        "user2": user2,
        "admin": admin,
    }


@pytest.fixture
async def service(session):
    """Создаём полноценный сервис с реальными репозиториями и фейковым S3."""
    srv = ExerciseServices(session)

    async def fake_upload(bucket, key, file, public):
        return f"https://fake-s3.local/{key}"

    async def fake_remove(bucket, key):
        return None

    srv.s3.upload_upload_file = fake_upload
    srv.s3.remove_file_url = fake_remove

    return srv


@pytest.mark.asyncio
async def test_parse_create_exercise_form_valid_time_mode():
    result = parse_create_exercise_form(
        title="Plank",
        type="static",
        description="Hold position",
        time_work=30,
        repetitions=None,
        count_sets=None,
        rest_sec=10
    )
    assert result.time_work == 30
    assert result.repetitions is None
    assert result.count_sets is None


@pytest.mark.asyncio
async def test_parse_create_exercise_form_valid_reps_mode():
    result = parse_create_exercise_form(
        title="Push Up",
        type="strength",
        description="Upper body",
        time_work=None,
        repetitions=20,
        count_sets=3,
        rest_sec=15
    )
    assert result.repetitions == 20
    assert result.count_sets == 3


@pytest.mark.asyncio
async def test_parse_create_exercise_form_no_mode():
    with pytest.raises(HTTPException) as e:
        parse_create_exercise_form(
            title="Jump",
            type="plyo",
            description="Explosive",
            time_work=None,
            repetitions=None,
            count_sets=None,
            rest_sec=None
        )
    assert "Specify either time_work" in str(e.value)


@pytest.mark.asyncio
async def test_parse_create_exercise_form_both_modes():
    with pytest.raises(HTTPException) as e:
        parse_create_exercise_form(
            title="Burpee",
            type="cardio",
            description="Full body",
            time_work=60,
            repetitions=10,
            count_sets=3,
            rest_sec=30
        )
    assert "Select one mode" in str(e.value)


@pytest.mark.asyncio
async def test_create_exercise_user_and_get_it(service, user, session):
    """Создаём упражнение и достаём его по id."""
    payload = CreateExerciseSchema(title="Push Up",
                                   type="strength",
                                   description="Upper body",
                                   time_work=None,
                                   repetitions=20,
                                   count_sets=3,
                                   rest_sec=15)
    fake_file = UploadFile(filename="pushup.mp4", file=BytesIO(b"video data"))
    user = user['user1']
    set_current_user(UserAdminGetModelSchema.model_validate(user))
    new_ex = await service.create_exercise(payload, fake_file)

    assert new_ex.id is not None
    assert new_ex.title == "Push Up"
    assert new_ex.user_id == user.id
    assert "https://fake-s3.local" in new_ex.media_url
    with pytest.raises(HTTPException) as e:
        for _ in range(PlanLimits.env_int("PLAN_COUNT_EXERCISE_FREE", 1)):
            await service.create_exercise(payload, fake_file)
    assert "You have reached the limit for creating exercise" in str(e.value)

    repo = ExerciseRepository(session)
    exercises, total = await repo.get_all_exercise_user(user.id, limit=10, start=0)
    assert total == 10
    assert exercises[0].title == "Push Up"


@pytest.mark.asyncio
async def test_create_exercise_admin_for_user_and_get_it(service, user, session):
    """Создаём упражнение и достаём его по id."""
    payload = CreateExerciseSchema(title="Push Up",
                                   type="strength",
                                   description="Upper body",
                                   time_work=None,
                                   repetitions=20,
                                   count_sets=3,
                                   rest_sec=15)
    fake_file = UploadFile(filename="pushup.mp4", file=BytesIO(b"video data"))
    admin = user['admin']
    user = user['user1']
    set_current_user(UserAdminGetModelSchema.model_validate(admin))
    new_ex = await service.create_exercise(payload, fake_file, user.id)

    assert new_ex.id is not None
    assert new_ex.title == "Push Up"
    assert new_ex.user_id == user.id
    assert "https://fake-s3.local" in new_ex.media_url
    for _ in range(PlanLimits.env_int("PLAN_COUNT_EXERCISE_FREE", 1) - 1):
        await service.create_exercise(payload, fake_file, user.id)
    with pytest.raises(HTTPException) as e:
        await service.create_exercise(payload, fake_file, user.id)
    assert "You have reached the limit for creating exercise" in str(e.value)
    repo = ExerciseRepository(session)
    exercises, total = await repo.get_all_exercise_user(user.id, limit=10, start=0)
    assert total == 10
    assert exercises[0].title == "Push Up"


@pytest.mark.asyncio
async def test_user_reaches_exercise_limit(service, user, session, monkeypatch):
    """Проверяем, что при превышении лимита выбрасывается _forbidden."""
    # Подменяем лимиты у пользователя (например, лимит = 1)
    limits = user.get_limits()
    monkeypatch.setattr(limits, "exercises_limit", 1)

    # Добавляем одно упражнение — всё ок
    payload = CreateExerciseSchema(title="Squat", description="Test")
    file = UploadFile(filename="squat.mp4", file=BytesIO(b"123"))
    await service.create_exercise(payload, file, user.id)

    # Второе — должно выбросить ошибку
    payload2 = CreateExerciseSchema(title="Push-up", description="Again")
    file2 = UploadFile(filename="pushup.mp4", file=BytesIO(b"video"))
    with pytest.raises(Exception) as e:
        await service.create_exercise(payload2, file2, user.id)
    assert "limit for creating exercise" in str(e.value)


@pytest.mark.asyncio
async def test_admin_ignores_limit(service, admin, session, monkeypatch):
    """Админ может создавать упражнения без ограничений."""
    set_current_user(admin)
    limits = admin.get_limits()
    monkeypatch.setattr(limits, "exercises_limit", 0)

    payload = CreateExerciseSchema(title="Pull Up", description="Admin test")
    file = UploadFile(filename="pullup.mp4", file=BytesIO(b"vid"))

    result = await service.create_exercise(payload, file, admin.id)
    assert result.user_id == admin.id
    assert "pullup.mp4" in result.media_url


@pytest.mark.asyncio
async def test_update_exercise_title(service, user, session):
    """Проверяем обновление упражнения."""
    payload = CreateExerciseSchema(title="Sit Up", description="Abs")
    file = UploadFile(filename="situp.mp4", file=BytesIO(b"vid"))
    created = await service.create_exercise(payload, file, user.id)

    update_payload = CreateExerciseSchema(title="Sit Up Advanced", description="Abs 2.0")
    updated = await service.update_exercise(created.id, update_payload)

    assert updated.title == "Sit Up Advanced"
    assert updated.description == "Abs 2.0"


@pytest.mark.asyncio
async def test_remove_exercise_deletes_from_db(service, user, session):
    """Удаление упражнения действительно убирает его из БД."""
    payload = CreateExerciseSchema(title="Jump", description="Plyometric")
    file = UploadFile(filename="jump.mp4", file=BytesIO(b"video"))
    created = await service.create_exercise(payload, file, user.id)

    await service.remove_exercise_from_all_workout(created.id)

    repo = ExerciseRepository(session)
    exercises, total = await repo.get_all_exercise_user(user.id, limit=10, start=0)
    assert total == 0
