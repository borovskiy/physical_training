import asyncio
from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# гарантируем, что корень проекта в sys.path
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# --- конфиг alembic ---
config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

# --- импортируем настройки и модели ---
from app.db.base import BaseModel  # noqa: E402
import app.db.models  # noqa: F401,E402
from app.core.config import settings

target_metadata = BaseModel.metadata
DB_URL = settings.DB_URL


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Sync функция для conn.run_sync()."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode (async)."""
    engine: AsyncEngine = create_async_engine(DB_URL, future=True)

    async with engine.connect() as conn:
        await conn.run_sync(do_run_migrations)

    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
