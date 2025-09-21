from math import ceil
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserModel, GroupModel
from db.schemas.group_schema import GroupCreateSchema, GroupMembersCreateSchema, GroupPage, GroupMembersAddSchema
from db.schemas.paginate_schema import PageMeta

from repositories.group_repositories import GroupRepository
from repositories.user_repository import UserRepository
from repositories.workout_repositories import WorkoutRepository
from services.auth_service import _forbidden
from utils.context import get_current_user
from core.config import settings


class GroupServices:
    def __init__(self, session: AsyncSession):
        self.workout_repo = WorkoutRepository(session)
        self.repo = GroupRepository(session)
        self.user_repo = UserRepository(session)

    async def create_group(self, group_schema: GroupCreateSchema):
        current_user = get_current_user()
        return await self.repo.add_group(group_schema.model_dump(), current_user.id)

    async def rename_group(self, group_id: int, group_name: str) -> GroupModel:
        current_user = get_current_user()
        group = await self.repo.get_group_by_id(group_id, current_user.id)
        if group is None:
            raise _forbidden("Not found group for you")
        await self.repo.rename_group(group_name, group_id)
        return await self.repo.get_group_by_id(group_id, current_user.id)

    async def delete_group(self, group_id: int):
        current_user = get_current_user()
        group = await self.repo.get_group_by_id(group_id, current_user.id)
        if group is None:
            raise _forbidden("Not found group for you")
        await self.repo.delete_group(group_id, current_user.id)
        return group

    async def add_members_in_group(self, id_group: int, members_schema: List[GroupMembersAddSchema]):
        current_user = get_current_user()
        list_members_id = {member.user_id for member in members_schema}
        group = await self.repo.get_group_by_id_with_full_relation(id_group, current_user.id)
        if group is None:
            raise _forbidden("Not found group for you")
        if len(group.members) >= settings.MAX_COUNT_MEMBERS_GROUP:
            raise _forbidden("You cannot add more users to this group")
        if list_members_id & {member.id for member in group.members if member is not None}:
            raise _forbidden(
                f"you are trying to add users that are already in the list {[member.email for member in group.members]}")
        result = await self.user_repo.find_count_by_id(list(list_members_id))
        if len(list_members_id) != result:
            raise _forbidden("Not fount user in list")

        return await self.repo.add_members_group(list(list_members_id), id_group, current_user.id)

    async def get_groups_user(self, limit: int, start: int) -> GroupPage:
        current_user = get_current_user()
        groups, total = await self.repo.get_groups_user(current_user.id, limit, start)
        pages = ceil(total / limit) if limit else 1
        return GroupPage(
            groups=groups,
            meta=PageMeta(total=total, limit=limit, pages=pages),
        )

    async def get_group_by_id(self, id_group: int) -> GroupModel:
        current_user = get_current_user()
        group = await self.repo.get_group_by_id_with_full_relation(id_group, current_user.id)
        if group is None:
            raise _forbidden("Not found group")
        return group

    async def delete_members(self, members: List[GroupMembersAddSchema], group_id: int) -> GroupModel:
        current_user = get_current_user()
        group = await self.repo.get_group_by_id(group_id, current_user.id)
        if group is None:
            raise _forbidden("Not found group")
        ids_members = [member.user_id for member in members]
        await self.repo.remove_member_group_id(ids_members, group_id)
        return await self.repo.get_group_by_id_with_full_relation(group_id, current_user.id)

    async def delete_workout_from_group(self, workout_id: int, group_id: int):
        current_user = get_current_user()
        group = await self.repo.get_group_by_id(group_id, current_user.id)
        if group is None:
            raise _forbidden("Not found group")
        if workout_id not in [member.workout_id for member in group.members]:
            raise _forbidden("Not found members")
        return await self.repo.remove_workout_from_group(group_id)

    async def add_workout_in_group(self, id_group: int, id_workout: int):
        current_user = get_current_user()
        workout = await self.workout_repo.get_workout_with_user(id_workout, current_user.id)
        if workout is None:
            raise _forbidden("Not found workout for you")
        group = await self.repo.get_group_by_id(id_group, current_user.id)
        if group is None:
            raise _forbidden("Not found group for you")

        return await self.repo.update_workout_in_group(id_group, id_workout, current_user.id)
