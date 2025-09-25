import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.db.schemas.auth_schema import TokenResponse
from core.dependencies import user_services
from db.schemas.user_schema import UserRegisterSchema
from services.user_versice import UserServices

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/signup", response_model=UserRegisterSchema)
async def signup(sign_up_user: UserRegisterSchema,
                 user_serv: Annotated[UserServices, Depends(user_services)],
                 ):
    """
    Минимальная регистрация:
    - принимает email/пароль
    - возвращает "фиктивный" токен
    """
    logger.info("Try get user service")
    result = await user_serv.create_user(sign_up_user)
    return result


@router.get("/confirm")
async def confirm_email(
        token: Annotated[str, Query(...)],
        user_serv: Annotated[UserServices, Depends(user_services)],
):
    logger.info("Try get user service")
    await user_serv.confirm_email(token)
    return {"message": "Email confirmed"}


@router.post("/login", response_model=TokenResponse)
async def login(
        data_user: UserRegisterSchema,
        user_serv: Annotated[UserServices, Depends(user_services)],
):
    """
    Минимальный логин:
    - проверяет email/пароль
    - возвращает "фиктивный" токен
    """
    logger.info("Try get user service")
    token = await user_serv.login_user(data_user)
    return TokenResponse(access_token=token)
