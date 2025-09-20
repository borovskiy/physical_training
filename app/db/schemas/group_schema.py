from typing import Sequence, List

from db.schemas.base_schema import BaseModelSchema, BaseIdSchema, BaseCreatedAndUpdateSchema
from db.schemas.paginate_schema import PageMeta
from db.schemas.user_schema import UserGetGroupSchema
from db.schemas.workout_schema import WorkoutGetOneSchema


class GroupMembersAddSchema(BaseModelSchema):
    """
    /add_members_in_group/{group_id}
    """
    user_id: int


class GroupCreateSchema(BaseModelSchema):
    """
    /create_group
    /rename_group/{group_id}
    """
    name: str


class GroupGetOneSchema(BaseIdSchema, BaseCreatedAndUpdateSchema, GroupCreateSchema):
    """
    /create_group
    /rename_group/{group_id}
    """
    pass


class GroupGetSchema(BaseIdSchema, BaseCreatedAndUpdateSchema, GroupCreateSchema):
    """
    /get_groups/{group_id}
    """
    user: UserGetGroupSchema
    members: List[UserGetGroupSchema] | None
    workout: WorkoutGetOneSchema | None


class GroupFullSchema(GroupGetSchema):
    """
    /delete_group/{group_id}
    """
    user_id: int


class GroupMembersCreateSchema(GroupMembersAddSchema, BaseIdSchema, BaseCreatedAndUpdateSchema):
    """
    /add_members_in_group/{group_id}
    """


class GroupPage(BaseModelSchema):
    """
    /get_groups
    """
    groups: Sequence[GroupGetSchema]
    meta: PageMeta
