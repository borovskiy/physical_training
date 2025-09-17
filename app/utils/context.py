from __future__ import annotations
from typing import Optional
from contextvars import ContextVar

from db.models import UserModel

_current_user: ContextVar[Optional[UserModel]] = ContextVar("current_user", default=None)

def set_current_user(user: UserModel) -> None:
    _current_user.set(user)

def get_current_user() -> UserModel:
    user = _current_user.get()
    if user is None:
        # Можно вернуть None, но удобнее явно падать, чтобы не скрывать ошибки
        raise RuntimeError("No current user in context")
    return user