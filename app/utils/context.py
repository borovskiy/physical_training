from __future__ import annotations
from typing import Optional
from contextvars import ContextVar

from db.schemas.user_schema import UserAdminGetModelSchema
from logging_conf import request_user_var
from utils.raises import _unauthorized

_current_user: ContextVar[Optional[UserAdminGetModelSchema]] = ContextVar("current_user", default=None)


def set_current_user(user: UserAdminGetModelSchema) -> None:
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


def get_current_user() -> UserAdminGetModelSchema:
    user = _current_user.get()
    if user is None:
        raise _unauthorized("No current user")
    return user
