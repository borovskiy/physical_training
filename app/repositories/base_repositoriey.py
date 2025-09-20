from sqlalchemy import select, func

from db.base import BaseModel


class BaseRepo:
    def get_limit(self):
        raise Exception("Not func")