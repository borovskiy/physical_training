from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseModelSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseIdSchema:
    id: int


class BaseCreatedAndUpdateSchema:
    created_at: datetime
    updated_at: datetime
