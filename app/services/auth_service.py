from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError, InvalidSignatureError, ExpiredSignatureError
from passlib.context import CryptContext

from app.core.config import settings

from db.models import User
from db.schemas.auth import PayloadToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)



def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_bearer = HTTPBearer(auto_error=False)



def issue_email_verify_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = PayloadToken(
        token_limit_verify=int((now + timedelta(minutes=settings.VERIFY_TOKEN_TTL_MIN)).timestamp()),
        time_now=int(now.timestamp()),
        user_id=user.id,
        type="email_verify")

    return jwt.encode(payload.model_dump(), settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def check_active_and_confirmed_user(user: User) -> bool | HTTPException:
    return active_user(user) and confirmed_user(user)


def active_user(user: User) -> bool | HTTPException:
    if not user.is_active:
        raise _unauthorized("User is not active")
    return True


def confirmed_user(user: User) -> bool | HTTPException:
    if not user.is_confirmed:
        raise _unauthorized("User is not confirmed")
    return True


def verify_email_for_confirm_email(token: str) -> PayloadToken:
    data = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    payload = PayloadToken(**data)
    if payload.type != "email_verify":
        raise ValueError("Wrong token type")
    return payload


def hash_password(plain_password: str) -> str:
    """
    Возвращает bcrypt-хэш для хранения в БД.
    Соль генерируется автоматически, вшита в результат.
    """
    return _pwd_ctx.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Сверяет присланный пароль с хэшем из БД.
    Возвращает True/False.
    """
    if not _pwd_ctx.verify(plain_password, password_hash):
        raise HTTPException(status_code=404, detail="Not valid password")
    return True


def _unauthorized(detail: str = "Not authenticated"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_bearer_token(
        credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise _unauthorized("Authorization header missing or not Bearer")
    return credentials.credentials


def verify_token(raw_token: str) -> PayloadToken:
    """
    Проверяем подпись, срок, набор клеймов и тип.
    Возвращает payload, если всё ок; иначе кидает 401.
    """
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


def _forbidden(detail: str = "Forbidden"):
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

def _ok(detail: str = "OK"):
    return HTTPException(status_code=status.HTTP_200_OK, detail=detail)



