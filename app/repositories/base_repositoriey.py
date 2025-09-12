from sqlalchemy import select, func

from db.base import Base


class BaseRepo:

    def get_limit(self):
        raise Exception("Not func")