from __future__ import annotations
from typing import Optional
from contextvars import ContextVar

from fastapi import HTTPException
from starlette import status

from app.db.models import UserModel
from logging_conf import request_user_var
from utils.raises import _unauthorized

_current_user: ContextVar[Optional[UserModel]] = ContextVar("current_user", default=None)


def set_current_user(user: UserModel) -> None:
    _current_user.set(user)
    try:
        val = None
        if hasattr(user, "email") and user.email:
            val = user.email
        elif hasattr(user, "id") and user.id is not None:
            val = f"id={user.id}"
        request_user_var.set(val or "-")
    except Exception:
        request_user_var.set("-")


def get_current_user() -> UserModel:
    user = _current_user.get()
    if user is None:
        raise _unauthorized("No current user")
    return user
