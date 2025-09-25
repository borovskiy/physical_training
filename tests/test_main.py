import os
import pytest
from sqlalchemy import create_engine

import db.models
from db.base import BaseModel


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    db_path = os.path.abspath("test_training.db")
    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    BaseModel.metadata.drop_all(bind=engine)
    BaseModel.metadata.create_all(bind=engine)

    yield engine
    engine.dispose()
