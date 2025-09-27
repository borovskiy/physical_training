from __future__ import annotations

from typing import List, Sequence

from fastapi import HTTPException
from sqlalchemy import select, delete, update, Row, RowMapping, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.models import UserModel
from repositories.base_repositoriey import BaseRepo


class UserRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.model = UserModel

    async def add_user(self, data: dict) -> UserModel:
        self.log.info("add_user %s ", data)
        obj = self.model(**data)  # создаём объект
        self.session.add(obj)  # добавляем в сессию
        await self.session.commit()  # фиксируем
        await self.session.refresh(obj)  # подтягиваем id и т.п. сгенерированные БД
        return obj

    async def find_user_email(self, mail: str) -> UserModel | None:
        self.log.info("find_user_email %s ", mail)
        stmt = select(self.model).where(self.model.email == mail)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def find_user_id(self, id_user: int) -> UserModel | None:
        self.log.info("find_user_id %s ", id_user)
        stmt = select(self.model).where(self.model.id == id_user)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def find_users_by_id(self, list_users_id: List[int]) -> Sequence[UserModel]:
        self.log.info("find_users_by_id %s ", list_users_id)
        stmt = select(self.model).where(self.model.id.in_(list_users_id))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_count_users_by_id(self, list_users_id: List[int]) -> int:
        self.log.info("find_count_users_by_id %s", list_users_id)
        if not list_users_id:
            return 0
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.id.in_(list_users_id))
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def remove_user_all(self) -> bool:
        self.log.info("remove_user_all")
        stmt = delete(self.model)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def remove_user_id(self, user_id: int) -> bool:
        self.log.info("remove_user_id %s", user_id)
        stmt = delete(self.model).where(self.model.id == user_id)
        await self.session.execute(stmt)
        await self.session.commit()
        if self.get_user_by_id(user_id) is None:
            return True
        return False

    async def get_user_by_id(self, user_id: int | str) -> UserModel | None:
        self.log.info("get_user_by_id %s", user_id)
        stmt = select(self.model).where(self.model.id == int(user_id))
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def update_is_confirmed_user(self, user_id):
        self.log.info("update_is_confirmed_user %s", user_id)
        stmt = update(self.model).where(self.model.id == user_id).values(is_confirmed=True)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_user(self, data, user_id: int):
        self.log.info("update_user by id %s data %s", user_id, data)
        stmt = update(self.model).where(self.model.id == user_id).values(**data)
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await self.session.commit()
        return await self.session.get(self.model, user_id)
