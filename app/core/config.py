import os
from dataclasses import dataclass

from pydantic_settings import BaseSettings

from db.models.user_model import PlanEnum


class Settings(BaseSettings):
    DB_URL: str
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
    SERVER: str

    class Config:
        env_file = "../sandy.env"
        env_file_encoding = "utf-8"


settings = Settings()


@dataclass(frozen=True)
class PlanLimits:
    groups_limit: int
    exercises_limit: int
    workouts_limit: int
    members_group_limit: int


def env_int(key: str, default: int):
    v = os.environ.get(key)
    try:
        return int(v) if v is not None else default
    except ValueError:
        return default


PLAN_LIMITS_BY_NAME = {
    "free": PlanLimits(
        groups_limit=env_int("PLAN_COUNT_GROUP_FREE", 3),
        exercises_limit=env_int("PLAN_COUNT_EXERCISE_FREE", 50),
        workouts_limit=env_int("PLAN_COUNT_WORKOUT_FREE", 50),
        members_group_limit=env_int("PLAN_COUNT_MEMBERS_GROUP_FREE", 3),
    ),
    "pro": PlanLimits(
        groups_limit=env_int("PLAN_COUNT_GROUP_PRO", 100),
        exercises_limit=env_int("PLAN_COUNT_EXERCISE_PRO", 2000),
        workouts_limit=env_int("PLAN_COUNT_WORKOUT_PRO", 2000),
        members_group_limit=env_int("PLAN_COUNT_MEMBERS_GROUP_PRO", 50),
    ),
}


def get_limits(plan: PlanEnum) -> PlanLimits:
    return PLAN_LIMITS_BY_NAME[plan.value]
