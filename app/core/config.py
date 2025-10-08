from typing import Optional
from urllib.parse import quote_plus

from pydantic import model_validator
from pydantic_settings import BaseSettings

from db.models.user_model import PlanEnum, PlanLimits


class Settings(BaseSettings):
    JWT_SECRET: str
    JWT_ALG: str
    VERIFY_TOKEN_TTL_MIN: int
    APP_BASE_URL: str

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    SMTP_FROM: str

    CLOUD_URL: str
    CLOUD_ACCESS_KEY: str
    CLOUD_SECRET_KEY: str
    CLOUD_REGION: str
    MAX_COUNT_MEMBERS_GROUP: int = 10

    PLAN_COUNT_GROUP_FREE: int
    PLAN_COUNT_EXERCISE_FREE: int
    PLAN_COUNT_WORKOUT_FREE: int
    PLAN_COUNT_MEMBERS_GROUP_FREE: int
    PLAN_COUNT_GROUP_PRO: int
    PLAN_COUNT_EXERCISE_PRO: int
    PLAN_COUNT_WORKOUT_PRO: int
    PLAN_COUNT_MEMBERS_GROUP_PRO: int

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_URL: Optional[str] = None
    CELERY_RESULT_DB_URL: Optional[str] = None  # sync для celery/flower (SQL backend)

    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    AMQP_URL: str
    REDIS_PASSWORD: str
    REDIS_URL: str
    TIMEZONE: str
    SERVER: str

    class Config:
        env_file = "../sandy.env"
        env_file_encoding = "utf-8"

    @model_validator(mode="after")
    def assemble_urls(self) -> "Settings":
        if not self.POSTGRES_URL:
            self.POSTGRES_URL = (
                "postgresql+asyncpg://"
                f"{quote_plus(self.POSTGRES_USER)}:"
                f"{quote_plus(self.POSTGRES_PASSWORD)}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{quote_plus(self.POSTGRES_DB)}"
            )
        if not self.CELERY_RESULT_DB_URL:
            self.CELERY_RESULT_DB_URL = (
                "db+postgresql+psycopg://"
                f"{quote_plus(self.POSTGRES_USER)}:{quote_plus(self.POSTGRES_PASSWORD)}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{quote_plus(self.POSTGRES_DB)}"
            )
        return self


settings = Settings()

PLAN_LIMITS_BY_NAME = {
    PlanEnum.free.name: PlanLimits(
        groups_limit=PlanLimits.env_int("PLAN_COUNT_GROUP_FREE", 1),
        exercises_limit=PlanLimits.env_int("PLAN_COUNT_EXERCISE_FREE", 1),
        workouts_limit=PlanLimits.env_int("PLAN_COUNT_WORKOUT_FREE", 1),
        members_group_limit=PlanLimits.env_int("PLAN_COUNT_MEMBERS_GROUP_FREE", 1),
    ),
    PlanEnum.pro.name: PlanLimits(
        groups_limit=PlanLimits.env_int("PLAN_COUNT_GROUP_PRO", 1),
        exercises_limit=PlanLimits.env_int("PLAN_COUNT_EXERCISE_PRO", 1),
        workouts_limit=PlanLimits.env_int("PLAN_COUNT_WORKOUT_PRO", 1),
        members_group_limit=PlanLimits.env_int("PLAN_COUNT_MEMBERS_GROUP_PRO", 1),
    ),
}
