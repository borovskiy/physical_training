import asyncio

from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.repositories.user_repository import UserRepository
from core.config import settings
from db.models import User
from db.schemas.user import UserRegisterSchema, UserPostModelUpdateSchema, UserAdminPutModelSchema
from services.auth_service import issue_email_verify_token, hash_password, verify_email_for_confirm_email, \
    check_active_and_confirmed_user
from utils.email import send_email


class UserServices:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def add_user(self, user: UserRegisterSchema):
        find_user = await self.repo.find_user_email(user.email)
        if find_user is None:
            user.password_hash = hash_password(user.password_hash)
            user_dict = user.model_dump()
            user = await self.repo.add_user(user_dict)
            token = issue_email_verify_token(user)
            link = f"{settings.APP_BASE_URL}/api/v1/auth/confirm?token={token}"
            html = f"""
              <p>Привет! Подтверди e-mail: <a href="{link}">{link}</a></p>
              <p>Ссылка действует {settings.VERIFY_TOKEN_TTL_MIN} минут.</p>
            """
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

    async def remove_all_user(self):
        await self.repo.remove_user_all()

    async def confirm_email(self, token: str):
        try:
            token_data = verify_email_for_confirm_email(token)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        await self.repo.update_is_confirmed_user(token_data.user_id)

    async def verify_user(self, user: UserRegisterSchema) -> str | None:
        user_db = await self.repo.find_user_email(user.email)
        if user_db is None:
            raise HTTPException(status_code=404, detail="User not found")

        if check_active_and_confirmed_user(user_db):
            return issue_email_verify_token(user_db)
        return None

    async def update_user_profile(self, user: UserPostModelUpdateSchema, current_user: User):
        update_user = await self.repo.update_profile_user(user.model_dump(), current_user.id)
        if update_user is not None:
            return update_user
        raise HTTPException(status_code=404, detail="User not found")

    async def update_user_profile_admin(self, user_id: int, user: UserAdminPutModelSchema):
        user_put = await self.repo.find_user_id(user_id)
        if user_put is None:
            raise HTTPException(status_code=404, detail="User not found")
        update_user = await self.repo.update_profile_user(user.model_dump(), user_id)
        if update_user is not None:
            return update_user
        raise HTTPException(status_code=404, detail="User not found")

    async def find_user(self, user_id: int):
        return await self.repo.find_user_id(user_id)

    async def remove_user(self, user_id: int):
        user_del = await self.repo.remove_user_id(user_id)
        return user_del