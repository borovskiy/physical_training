from typing import Annotated, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from datetime import datetime, timedelta, timezone
from core.config import settings
from core.s3_cloud_connector import S3CloudConnector
from db.models import UserModel
from db.schemas.user_schema import UserAdminGetModelSchema
from services.auth_service import get_bearer_token, verify_token, check_active_and_confirmed_user
from services.exercise_service import ExerciseServices
from services.group_service import GroupServices
from services.user_versice import UserServices
from services.workout_service import WorkoutServices
from utils.context import set_current_user
from utils.raises import _forbidden, _unauthorized

SessionLocal = async_sessionmaker(
    bind=create_async_engine(settings.POSTGRES_URL, echo=False, ),
    expire_on_commit=False,
)


async def get_db():
    async with SessionLocal() as session:
        yield session


def user_services(session: AsyncSession = Depends(get_db)) -> UserServices:
    return UserServices(session)


def exercise_services(session: AsyncSession = Depends(get_db)) -> ExerciseServices:
    return ExerciseServices(session)


def workout_services(session: AsyncSession = Depends(get_db)) -> WorkoutServices:
    return WorkoutServices(session)


def group_services(session: AsyncSession = Depends(get_db)) -> GroupServices:
    return GroupServices(session)


def get_s3_connector() -> S3CloudConnector:
    return S3CloudConnector()


def require_user_attrs(
        is_admin: Optional[bool] = False,
):
    async def dep(current_user: Annotated[
        UserAdminGetModelSchema, Depends(get_current_user_from_token)]) -> UserAdminGetModelSchema:
        if is_admin:
            if bool(current_user.is_admin):
                return current_user
            else:
                raise _forbidden("Forbidden")
        else:
            return current_user

    return dep


async def get_current_user_from_token(
        raw_token: str = Depends(get_bearer_token),
        user_serv=Depends(user_services),
) -> UserAdminGetModelSchema:
    payload = verify_token(raw_token)
    user = await user_serv.repo.get_user_by_id(payload.user_id)
    if not user:
        raise _unauthorized("User not found")
    if user.token is None:
        raise _unauthorized("Token is not valid")
    if raw_token != user.token.token:
        raise _unauthorized("Token is not valid")
    if payload.token_limit_verify - datetime.now(timezone.utc).timestamp() < 0:
        await user_serv.repo.remove_token_user(payload.user_id)
        raise _unauthorized("Token timed out")
    if not await check_active_and_confirmed_user(user):
        raise _unauthorized("User is inactive or not confirmed")
    user_model = UserAdminGetModelSchema.model_validate(user)
    set_current_user(user_model)
    return user_model
