from datetime import datetime

from pydantic import ConfigDict

from db.models.user_model import PlanEnum
from db.schemas.base_schema import BaseCreatedAndUpdateSchema, BaseIdSchema, BaseModelSchema


class UserRegisterSchema(BaseModelSchema):
    email: str
    password_hash: str


class UserPostModelUpdateSchema(BaseModelSchema):
    first_name: str | None
    last_name: str | None
    birth_data: datetime | None


class UserGetGroupSchema(UserPostModelUpdateSchema):
    email: str


class UserGetModelSchema(UserPostModelUpdateSchema):
    plan: PlanEnum


class PasswordUserSchema(BaseModelSchema):
    password_hash: str


class SystemUserSchema(BaseModelSchema):
    email: str
    is_active: bool
    is_confirmed: bool
    is_admin: bool


class UserAdminGetModelSchema(BaseIdSchema, BaseCreatedAndUpdateSchema, UserGetModelSchema, SystemUserSchema):
    model_config = {"from_attributes": True}


class UserAdminPutModelSchema(UserGetModelSchema, SystemUserSchema):
    model_config = {"from_attributes": True}
