from typing import Sequence, List

from db.schemas.base import BaseModelSchema, BaseIdSchema, BaseCreatedAndUpdateSchema
from db.schemas.paginate import PageMeta
from db.schemas.user import UserGetGroupSchema


class GroupMembersAddSchema(BaseModelSchema):
    user_id: int


class GroupMembersGetSchema(BaseModelSchema):
    user: UserGetGroupSchema


class GroupCreateSchema(BaseModelSchema):
    name: str


class GroupGetSchema(BaseIdSchema, BaseCreatedAndUpdateSchema, GroupCreateSchema):
    user_id: int


class GroupFullSchema(GroupGetSchema):
    user_id: int
    members: List[GroupMembersGetSchema]


class GroupMembersCreateSchema(GroupMembersAddSchema, BaseIdSchema, BaseCreatedAndUpdateSchema):
    ...

class GroupPage(BaseModelSchema):
    groups: Sequence[GroupGetSchema]
    meta: PageMeta
