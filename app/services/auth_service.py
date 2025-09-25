import logging
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError, InvalidSignatureError, ExpiredSignatureError
from passlib.context import CryptContext

from app.core.config import settings

from db.models import UserModel
from db.models.user_model import TypeTokensEnum
from db.schemas.auth_schema import PayloadToken
from utils.raises import _unauthorized

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security_bearer = HTTPBearer(auto_error=False)

logger = logging.getLogger(__name__)


async def issue_email_verify_token(user: UserModel, type_token: TypeTokensEnum = TypeTokensEnum.email_verify) -> str:
    logger.info("Issue email verify token")
    now = datetime.now(timezone.utc)
    payload = PayloadToken(
        token_limit_verify=int((now + timedelta(minutes=settings.VERIFY_TOKEN_TTL_MIN)).timestamp()),
        time_now=int(now.timestamp()),
        user_id=user.id,
        type=type_token.name)

    return jwt.encode(payload.model_dump(), settings.JWT_SECRET, algorithm=settings.JWT_ALG)


async def check_active_and_confirmed_user(user: UserModel) -> bool | HTTPException:
    logger.info("Check active and confirmed user")
    return await check_active_user(user) and await check_confirmed_user(user)


async def check_active_user(user: UserModel) -> bool | HTTPException:
    logger.info("Check active user")
    if not user.is_active:
        logger.error("User is not active")
        raise _unauthorized("User is not active")
    return True


async def check_confirmed_user(user: UserModel) -> bool | HTTPException:
    logger.info("Check confirmed user")
    if not user.is_confirmed or user.is_confirmed == False:
        logger.error("User is not confirmed")
        raise _unauthorized("User is not confirmed")
    return True


async def hash_password(plain: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain.encode(), salt).decode()


async def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


async def get_bearer_token(
        credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
) -> str:
    logger.info("Get bearer token")
    if not credentials or credentials.scheme.lower() != "bearer":
        logger.error("Authorization header missing or not Bearer")
        raise _unauthorized("Authorization header missing or not Bearer")
    return credentials.credentials


def verify_token(raw_token: str) -> PayloadToken:
    logger.info("verify token")
    try:
        payload = jwt.decode(
            raw_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
        )
    except ExpiredSignatureError:
        logger.error("Token expired")
        raise _unauthorized("Token expired")
    except InvalidSignatureError:
        logger.error("Invalid signature")
        raise _unauthorized("Invalid signature")
    except InvalidTokenError:
        logger.error("Invalid token")
        raise _unauthorized("Invalid token")
    payload = PayloadToken(**payload)
    logger.error("Payload Token")
    return payload
