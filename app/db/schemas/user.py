from datetime import datetime

from pydantic import BaseModel, ConfigDict

from db.models.user import PlanEnum


class UserIdSchema(BaseModel):
    id: int


class UserCreatedAndUpdateSchema(BaseModel):
    created_at: datetime
    updated_at: datetime


class UserRegisterSchema(BaseModel):
    email: str
    password_hash: str
    model_config = ConfigDict(from_attributes=True)


class UserPostModelUpdateSchema(BaseModel):
    first_name: str | None
    last_name: str | None
    birth_data: datetime | None

    model_config = ConfigDict(from_attributes=True)


class UserGetModelSchema(UserPostModelUpdateSchema):
    plan: PlanEnum


class PasswordUserSchema(BaseModel):
    password_hash: str


class SystemUserSchema(BaseModel):
    email: str
    is_active: bool
    is_confirmed: bool
    is_admin: bool
    model_config = ConfigDict(from_attributes=True)


class UserAdminGetModelSchema(UserGetModelSchema, SystemUserSchema, UserIdSchema, UserCreatedAndUpdateSchema):
    model_config = {"from_attributes": True}


class UserAdminPutModelSchema(UserGetModelSchema, SystemUserSchema):
    model_config = {"from_attributes": True}
