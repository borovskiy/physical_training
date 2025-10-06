import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import clear_mappers
from db.base import BaseModel
from repositories.user_repository import UserRepository


@pytest.fixture(scope="session")
def event_loop():
    """
    Переопределяем event loop, чтобы pytest мог запускать асинхронные тесты.
    По умолчанию pytest-asyncio требует этот фикстур.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_engine():
    """
    Создаем асинхронный движок SQLAlchemy с in-memory SQLite базой.
    Это временная база, которая живёт только во время тестов.
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield engine
    await engine.dispose()
    clear_mappers()


@pytest.fixture()
async def session(async_engine):
    """
    Создаём новую сессию SQLAlchemy для каждого теста.
    Это важно — чтобы данные не "перетекали" между тестами.
    """
    async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture()
async def user_repo(session):
    """
    Создаём экземпляр UserRepository, передавая ему тестовую сессию.
    """
    return UserRepository(session)
