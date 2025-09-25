import logging
from datetime import datetime, timedelta, timezone

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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security_bearer = HTTPBearer(auto_error=False)

logger = logging.getLogger(__name__)


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def issue_email_verify_token(user: UserModel, type_token: TypeTokensEnum = TypeTokensEnum.email_verify) -> str:
    now = datetime.now(timezone.utc)
    payload = PayloadToken(
        token_limit_verify=int((now + timedelta(minutes=settings.VERIFY_TOKEN_TTL_MIN)).timestamp()),
        time_now=int(now.timestamp()),
        user_id=user.id,
        type=type_token.name)

    return jwt.encode(payload.model_dump(), settings.JWT_SECRET, algorithm=settings.JWT_ALG)


async def check_active_and_confirmed_user(user: UserModel) -> bool | HTTPException:
    return await active_user(user) and await confirmed_user(user)


async def active_user(user: UserModel) -> bool | HTTPException:
    if not user.is_active:
        raise _unauthorized("User is not active")
    return True


async def confirmed_user(user: UserModel) -> bool | HTTPException:
    if not user.is_confirmed or user.is_confirmed == False:
        raise _unauthorized("User is not confirmed")
    return True


def get_password_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


async def get_bearer_token(
        credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise _unauthorized("Authorization header missing or not Bearer")
    return credentials.credentials


def verify_token(raw_token: str) -> PayloadToken:
    try:
        payload = jwt.decode(
            raw_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
        )
    except ExpiredSignatureError:
        raise _unauthorized("Token expired")
    except InvalidSignatureError:
        raise _unauthorized("Invalid signature")
    except InvalidTokenError:
        raise _unauthorized("Invalid token")
    payload = PayloadToken(**payload)
    return payload
