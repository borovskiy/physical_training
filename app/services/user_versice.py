from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.enums import TypeTokensEnum
from db.schemas.auth_schema import TokenResponse
from repositories.user_repository import UserRepository
from db.models import UserModel
from db.schemas.qeue_schemas import QeueSignupUserSchema
from db.schemas.user_schema import UserRegisterSchema, UserPostModelUpdateSchema, UserAdminPutModelSchema
from services.auth_service import AuthServ

from services.base_services import BaseServices
from utils.context import get_current_user
from utils.raises import _forbidden, _ok, _bad_request, _conflict, _unauthorized, _not_found
from celery_app import celery_app


class UserServices(BaseServices):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.repo = UserRepository(session)

    async def create_user(self, user: UserRegisterSchema) -> bool:
        self.log.info("create_user")
        find_user = await self.repo.find_user_email(user.email)
        if find_user is None:
            user.password_hash = await AuthServ.hash_password(user.password_hash)
            user_dict = user.model_dump()
            user = await self.repo.create_one_obj_model(user_dict)
            token = await AuthServ.issue_email_verify_token(user.id, TypeTokensEnum.email_verify)
            self.log.info("Create token for registration ", )
            data = QeueSignupUserSchema(token=token, email_to=user.email, subject="Подтверждение e-mail", )
            celery_app.send_task(name='tasks.email_tasks.send_signup_email_task', args=(data.model_dump(),),
                                 queue="test_queues")
            return True
        raise _conflict(f"User with email: {user.email} exists")

    async def confirm_email(self, token: str):
        try:
            token_data = AuthServ.verify_token(token)
            if token_data.type != TypeTokensEnum.email_verify.name:
                self.log.warning("Wrong token type")
                raise ValueError("Wrong token type")
        except Exception:
            self.log.warning("Invalid or expired token")
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        await self.repo.update_is_confirmed_user(token_data.user_id)

    async def login_user(self, user_email: str, user_password_hash: str) -> str | None:
        self.log.info("Try login user %s ", user_email)
        user_db = await self.repo.find_user_email(user_email)
        if user_db is None:
            self.log.warning("User not found")
            raise HTTPException(status_code=404, detail="User not found")
        self.log.info("Find user email %s ", user_email)
        if not await AuthServ.verify_password(user_password_hash, user_db.password_hash):
            self.log.warn("Wrong password")
            raise _forbidden("Wrong password")
        if await AuthServ.check_active_and_confirmed_user(user_db):
            if user_db.token is not None:
                payload = AuthServ.verify_token(user_db.token.token)
                if payload.token_limit_verify - datetime.now(timezone.utc).timestamp() < 0:
                    return await self.repo.update_token_user(
                        await AuthServ.issue_email_verify_token(user_db.id, TypeTokensEnum.access), user_db.id)
                return user_db.token.token
            return await self.repo.add_token_user(
                await AuthServ.issue_email_verify_token(user_db.id, TypeTokensEnum.access), user_db.id)
        raise _unauthorized("User is not active")

    async def update_user_profile(self, user_schema: UserPostModelUpdateSchema, user_id: int):
        self.log.info("update user profile")
        update_user = await self.repo.update_user(user_schema.model_dump(), user_id)
        if update_user is not None:
            self.log.info("update user %s", update_user)
            return update_user
        self.log.warning("User not found")
        raise HTTPException(status_code=404, detail="User not found")

    async def update_user_admin(self, user_id: int, user: UserAdminPutModelSchema) -> UserModel | None:
        self.log.info("update_user_admin")
        user_put = await self.repo.find_user_id(user_id)
        if user_put is None:
            self.log.warning("User not found")
            raise _not_found("User not found")
        update_user = await self.repo.update_user(user.model_dump(), user_id)
        if update_user is None:
            self.log.warning("User not found")
            raise _not_found("User not found")
        self.log.info("user", update_user.email)
        return update_user

    async def find_user(self, user_id: int) -> UserModel:
        self.log.info("find_user")
        return await self.repo.find_user_id(user_id)

    async def remove_user(self, user_id: int) -> HTTPException:
        self.log.info("remove_user")
        if await self.repo.remove_user_id(user_id):
            self.log.info("User remove")
            return _ok("User remove")
        else:
            self.log.warning("User not remove")
            return _bad_request("User not remove")

    async def refresh_token(self) -> TokenResponse:
        current_user = get_current_user()
        await self.repo.remove_token_user(current_user.id)
        token: str = await AuthServ.issue_email_verify_token(current_user.id, TypeTokensEnum.access)
        return TokenResponse(access_token=await self.repo.add_token_user(token, current_user.id))
