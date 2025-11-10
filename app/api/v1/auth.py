import logging
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, Query

from db.schemas.auth_schema import TokenResponse
from core.dependencies import user_services, require_user_attrs
from db.schemas.user_schema import UserRegisterSchema
from services.auth_service import AuthServ
from services.user_versice import UserServices
from utils.context import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/healthcheck", status_code=200)
async def healthcheck():
    return {"status": "OK"}


@router.post("/signup", response_model=bool, status_code=201)
async def signup(sign_up_user: UserRegisterSchema,
                 user_serv: Annotated[UserServices, Depends(user_services)],
                 ):
    """
    Minimum registration:
    - accepts email/password
    - returns token
    """
    logger.info("Try get user service")
    return await user_serv.create_user(sign_up_user)


@router.get("/confirm")
async def confirm_email(
        token: Annotated[str, Query(...)],
        user_serv: Annotated[UserServices, Depends(user_services)],
):
    """
    Confirmation of the registered user
    """
    logger.info("Try get user service")
    await user_serv.confirm_email(token)
    return {"message": "Email confirmed"}


@router.post("/login", response_model=TokenResponse)
async def login(
        data_user: UserRegisterSchema,
        user_serv: Annotated[UserServices, Depends(user_services)],
):
    """
    User login:
    - checks email/password
    - returns token
    """
    logger.info("Try get user service")
    token = await user_serv.login_user(data_user.email, data_user.password_hash)
    return TokenResponse(access_token=token)


@router.post("/refresh_token", response_model=TokenResponse, dependencies=[Depends(require_user_attrs())])
async def refresh_token(
        user_serv: Annotated[UserServices, Depends(user_services)],
):
    """
    In case you become aware of a token leak, this will help you change it
    """
    logger.info("Try get user service")
    return await user_serv.refresh_token()


from fastapi import APIRouter, Request, HTTPException


@router.post("/validate-token")
async def validate_token(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split(" ")[1]
    try:
        payload = AuthServ.verify_token(token)
        # тут можно проверить blacklist
        return {"user_id": payload.get("sub"), "roles": payload.get("roles", [])}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
