from __future__ import annotations

from typing import List

from sqlalchemy import select, delete, update, func, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from db.models import UserModel
from db.models.jwt_token_model import JWTTokenModel
from repositories.base_repositoriey import BaseRepo
from utils.raises import _not_found


class UserRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = UserModel
        self.token_model = JWTTokenModel

    async def find_user_email(self, mail: str) -> UserModel | None:
        self.log.info("find_user_email %s ", mail)
        stmt = select(self.model).where(self.model.email == mail).options(joinedload(self.model.token))
        return await self.execute_session_get_one(stmt)

    async def find_user_id(self, id_user: int, need_token: bool = False) -> UserModel | Exception:
        self.log.info("find_user_id %s ", id_user)
        stmt = select(self.model).where(self.model.id == id_user)
        if need_token:
            stmt = stmt.options(joinedload(self.model.token))
        result_user = await self.execute_session_get_one(stmt)
        if result_user is None:
            raise _not_found('User not found')
        return result_user

    async def find_count_users_by_id(self, list_users_id: List[int]) -> int:
        self.log.info("find_count_users_by_id %s", list_users_id)
        if not list_users_id:
            return 0
        stmt = select(func.count()).select_from(self.model).where(self.model.id.in_(list_users_id))
        return await self.execute_session_get_one(stmt)

    async def remove_user_id(self, user_id: int) -> bool:
        self.log.info("remove_user_id %s", user_id)
        stmt = delete(self.model).where(self.model.id == user_id)
        await self.execute_session_and_commit(stmt)
        if self.find_user_id(user_id) is None:
            return True
        return False

    async def update_is_confirmed_user(self, user_id):
        self.log.info("update_is_confirmed_user %s", user_id)
        stmt = update(self.model).where(self.model.id == user_id).values(is_confirmed=True)
        await self.execute_session_and_commit(stmt)

    async def update_user(self, data, user_id: int) -> UserModel:
        self.log.info("update_user by id %s data %s", user_id, data)
        stmt = update(self.model).where(self.model.id == user_id).values(**data)
        await self.execute_session_and_commit(stmt)
        return await self.find_user_id(user_id)

    async def add_token_user(self, token: str, user_id: int) -> str | None:
        self.log.info("add_token_user by id %s ", user_id)
        obj = JWTTokenModel(token=token, user_id=user_id)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj.token

    async def update_token_user(self, token: str, user_id: int) -> str | None:
        self.log.info("update_token_user by id %s ", user_id)
        stmt = update(self.token_model).where(self.token_model.user_id == user_id).values(token=token)
        await self.execute_session_and_commit(stmt)
        return token

    async def remove_token_user(self, user_id: int) -> str | None:
        self.log.info("remove_token_user by id %s ", user_id)
        stmt = delete(self.token_model).where(self.token_model.user_id == user_id)
        await self.execute_session_and_commit(stmt)
