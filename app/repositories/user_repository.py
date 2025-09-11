from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = User

    async def add_user(self, data: dict) -> User:
        obj = self.model(**data)  # создаём объект
        self.session.add(obj)  # добавляем в сессию
        await self.session.commit()  # фиксируем
        await self.session.refresh(obj)  # подтягиваем id и т.п. сгенерированные БД
        return obj

    async def find_user_email(self, mail: str) -> User | None:
        stmt = select(self.model).where(User.email == mail)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def find_user_id(self, id_user: int) -> User | None:
        stmt = select(self.model).where(User.id == id_user)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def remove_user_all(self) -> bool:
        stmt = delete(self.model)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_by_id(self, user_id: int | str) -> User | None:
        stmt = select(self.model).where(self.model.id == int(user_id))
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def update_is_confirmed_user(self, user_id):
        stmt = update(User).where(User.id == user_id).values(is_confirmed=True)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_profile_user(self, data, user_id: int):
        stmt = update(User).where(User.id == user_id).values(**data)
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await self.session.commit()
        return await self.session.get(User, user_id)
