import logging
from abc import ABC
from typing import Type, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from utils.raises import _bad_request


class BaseRepo(ABC):
    def __init__(self, session: AsyncSession):
        self.log = logging.LoggerAdapter(
            logging.getLogger(__name__),
            {"component": self.__class__.__name__}
        )
        self.session = session
        self.model = None

    async def create_one_obj_model(self, data: dict):
        self.log.info(f"create_one_obj_model")
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_one_obj_model(self, id_model: int):
        self.log.info("get_one_obj_model id %s", id_model)
        stmt_exercise = select(self.model).where(self.model.id == id_model)
        res = await self.session.execute(stmt_exercise)
        return res.scalars().first()

    async def execute_session_get_all(self, stmt):
        try:
            self.log.info("execute_session_get_all")
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as ex:
            self.log.error("error execute stmt %s", stmt)
            self.log.error("Exception %s", ex)
            raise _bad_request("Unexpected error")

    async def execute_session_get_one(self, stmt):
        try:
            self.log.info("execute_session_get_one")
            result = await self.session.execute(stmt)
            return result.scalars().one_or_none()
        except Exception as ex:
            self.log.error("error execute stmt %s", stmt)
            self.log.error("Exception %s", ex)
            raise _bad_request("Unexpected error")

    async def execute_session_get_first(self, stmt):
        try:
            self.log.info("execute_session_get_first")
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except Exception as ex:
            self.log.error("error execute stmt %s", stmt)
            self.log.error("Exception %s", ex)
            raise _bad_request("Unexpected error")

    async def execute_session_and_commit(self, stmt):
        try:
            self.log.info("execute_session_and_commit")
            await self.session.execute(stmt)
            await self.session.commit()
        except Exception as ex:
            self.log.error("error execute stmt %s", stmt)
            self.log.error("Exception %s", ex)
            raise _bad_request("Unexpected error")
