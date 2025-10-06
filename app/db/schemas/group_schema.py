from typing import Sequence, List, Optional, Annotated

from pydantic import Field

from db.schemas.base_schema import BaseModelSchema, BaseIdSchema, BaseCreatedAndUpdateSchema
from db.schemas.paginate_schema import PageMeta
from db.schemas.user_schema import UserGetGroupSchema
from db.schemas.workout_schema import WorkoutCreateSchema


class GroupMembersAddSchema(BaseModelSchema):
    """
    /add_members_in_group/{group_id}
    /remove_members_from_group/{member_id}/{group_id}
    """
    user_id: int


class GroupCreateSchema(BaseModelSchema):
    """
    /create_group
    /rename_group/{group_id}
    """
    name: str
    _user_id: int | None = None

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if self._user_id is not None:
            data["user_id"] = self._user_id
        return data


class GroupGetOneSchema(BaseIdSchema, BaseCreatedAndUpdateSchema, GroupCreateSchema):
    """
    /create_group
    /rename_group/{group_id}
    /get_groups
    """
    pass


class GroupGetSchema(BaseIdSchema, BaseCreatedAndUpdateSchema, GroupCreateSchema):
    """
    /get_groups/{group_id}
    """
    user: UserGetGroupSchema
    members: List[UserGetGroupSchema] | None
    workout: WorkoutCreateSchema | None


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
    groups: Sequence[GroupGetOneSchema]
    meta: PageMeta
