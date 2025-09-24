from datetime import datetime, timedelta, timezone
from contextlib import nullcontext as does_not_raise
import jwt
import pytest
from fastapi import HTTPException

from app.services.auth_service import get_password_hash, verify_password, issue_email_verify_token, active_user, \
    confirmed_user, check_active_and_confirmed_user

from core.config import settings
from db.models import UserModel
from db.models.user_model import PlanEnum, TypeTokensEnum


@pytest.fixture(scope="class")
def user_factory():
    def make_user(**overrides):
        base = dict(
            id=1,
            email="test@example.com",
            is_admin=False,
            password_hash="hashed",
            first_name="Test",
            last_name="User",
            is_active=True,
            is_confirmed=False,
            plan=PlanEnum.free,
        )
        base.update(overrides)
        return UserModel(**base)

    return make_user


class TestAuthClass:

    @pytest.mark.asyncio
    async def test_verify_password(self):
        password_str = "password"
        wrong_str = "wrong"
        h = get_password_hash(password_str)
        assert await verify_password(password_str, h)
        assert not await verify_password(wrong_str, h)
        assert h.startswith("$2b$12$")

    @pytest.mark.asyncio
    async def test_issue_email_verify_token(self, monkeypatch, user_fixture):
        t0 = datetime.now(timezone.utc)
        token = await issue_email_verify_token(user_fixture, TypeTokensEnum.access)

        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
            options={"verify_exp": False},
        )

        assert payload["user_id"] == user_fixture.id
        assert payload["type"] == TypeTokensEnum.access.name

        now_claim = datetime.fromtimestamp(payload["time_now"], tz=timezone.utc)
        limit_claim = datetime.fromtimestamp(payload["token_limit_verify"], tz=timezone.utc)

        assert abs((now_claim - t0).total_seconds()) <= 5
        expected_limit = t0 + timedelta(minutes=settings.VERIFY_TOKEN_TTL_MIN)
        assert abs((limit_claim - expected_limit).total_seconds()) <= 5

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "is_active,result, ctx",
        [
            (True, True, does_not_raise()),
            (False, False, pytest.raises(HTTPException)),
        ],
    )
    async def test_active_user(self, user_factory, is_active, result, ctx):
        user = user_factory(is_active=is_active)
        with ctx:
            assert await active_user(user) is result

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "is_confirmed,result, ctx",
        [
            (True, True, does_not_raise()),
            (False, False, pytest.raises(HTTPException)),
        ],
    )
    async def test_confirmed_user(self, user_factory, result, is_confirmed, ctx):
        user = user_factory(is_confirmed=is_confirmed)
        with ctx:
            assert await confirmed_user(user) is result

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "is_active, is_confirmed, result, ctx",
        [
            (False, True, False, pytest.raises(HTTPException)),
            (True, False, False, pytest.raises(HTTPException)),
            (True, True, True, does_not_raise()),
        ],
    )
    async def test_check_active_and_confirmed_user(self, user_factory, is_active, is_confirmed, result, ctx):
        user = user_factory(is_active=is_active, is_confirmed=is_confirmed)
        with ctx:
            assert await check_active_and_confirmed_user(user) is result
