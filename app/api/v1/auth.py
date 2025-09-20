from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.db.schemas.auth_schema import TokenResponse
from core.dependencies import user_services
from db.schemas.user_schema import UserRegisterSchema
from services.user_versice import UserServices

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
    result = await user_serv.create_user(sign_up_user)

    return result


# @router.get("/remove_all_user")
# async def remove_all_user(
#         user_serv: Annotated[UserServices, Depends(user_services)],
# ):
#     await user_serv.remove_all_user()
#
#     return {"message": "Users removed"}


@router.get("/confirm")
async def confirm_email(
        token: Annotated[str, Query(...)],
        user_serv: Annotated[UserServices, Depends(user_services)],
):
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
    token = await user_serv.login_user(data_user)
    return TokenResponse(access_token=token)
