from datetime import datetime

from pydantic import ConfigDict
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
