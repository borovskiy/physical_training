import asyncio

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.repositories.user_repository import UserRepository
from core.config import settings
from db.models import UserModel
from db.models.user_model import TypeTokensEnum
from db.schemas.user_schema import UserRegisterSchema, UserPostModelUpdateSchema, UserAdminPutModelSchema
from services.auth_service import issue_email_verify_token, get_password_hash, check_active_and_confirmed_user, \
    _unauthorized, verify_password, verify_token
from services.base_services import BaseServices
from utils.context import get_current_user
from utils.email import send_email
from utils.raises import _forbidden, _ok, _bad_request


class UserServices(BaseServices):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.repo = UserRepository(session)

    async def create_user(self, user: UserRegisterSchema):
        find_user = await self.repo.find_user_email(user.email)
        self.log.info("Find user %s", find_user.email)
        if find_user is None:
            user.password_hash = get_password_hash(user.password_hash)
            user_dict = user.model_dump()
            user = await self.repo.add_user(user_dict)
            token = issue_email_verify_token(user, TypeTokensEnum.email_verify)
            self.log.info("Create token for registration %s", token)
            link = f"{settings.APP_BASE_URL}/api/v1/auth/confirm?token={token}"
            html = f"""
              <p>Привет! Подтверди e-mail: <a href="{link}">{link}</a></p>
              <p>Ссылка действует {settings.VERIFY_TOKEN_TTL_MIN} минут.</p>
            """
            self.log.info("Send email")
            asyncio.create_task(
                send_email(
                    to=user.email,
                    subject="Подтверждение e-mail",
                    html=html,
                    text=f"Confirm: {link}",
                )
            )
            return user
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User with email: {user.email} exists")

    async def confirm_email(self, token: str):
        try:
            token_data = verify_token(token)
            if token_data.type != TypeTokensEnum.email_verify.name:
                self.log.error("Wrong token type")
                raise ValueError("Wrong token type")
        except Exception:
            self.log.error("Invalid or expired token")
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        await self.repo.update_is_confirmed_user(token_data.user_id)

    async def login_user(self, user: UserRegisterSchema) -> str | None:
        self.log.info("Try login user %s ", user)
        user_db = await self.repo.find_user_email(user.email)
        self.log.info("Find user email %s ", user)
        if user_db is None:
            self.log.error("User not found")
            raise HTTPException(status_code=404, detail="User not found")
        if await verify_password(user.password_hash, user_db.password_hash) is False:
            if user_db is None:
                self.log.error("Wrong password")
                raise _forbidden("Wrong password")
        if await check_active_and_confirmed_user(user_db):
            return await issue_email_verify_token(user_db, TypeTokensEnum.access)
        raise _unauthorized("User is not active")

    async def update_user_profile(self, user_schema: UserPostModelUpdateSchema):
        self.log.info("update user profile %s", user_schema)
        current_user = get_current_user()
        update_user = await self.repo.update_user(user_schema.model_dump(), current_user.id)
        if update_user is not None:
            self.log.info("update user %s", update_user)
            return update_user
        self.log.error("User not found")
        raise HTTPException(status_code=404, detail="User not found")

    async def update_user_admin(self, user_id: int, user: UserAdminPutModelSchema):
        self.log.info("update_user_admin id %s data %s", user_id, user.model_dump())
        user_put = await self.repo.find_user_id(user_id)
        if user_put is None:
            self.log.error("User not found")
            raise HTTPException(status_code=404, detail="User not found")
        update_user = await self.repo.update_user(user.model_dump(), user_id)
        if update_user is not None:
            self.log.info("user %s", update_user)
            return update_user
        self.log.error("User not found")
        raise HTTPException(status_code=404, detail="User not found")

    async def find_user(self, user_id: int) -> UserModel:
        self.log.info("find_user")
        return await self.repo.find_user_id(user_id)

    async def remove_user(self, user_id: int) -> HTTPException:
        self.log.info("remove_user")
        if await self.repo.remove_user_id(user_id):
            self.log.info("User remove")
            return _ok("User remove")
        else:
            self.log.error("User not remove")
            return _bad_request("User not remove")
