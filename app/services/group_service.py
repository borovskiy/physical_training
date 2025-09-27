from math import ceil
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import GroupModel
from db.schemas.group_schema import GroupCreateSchema, GroupPage, GroupMembersAddSchema
from db.schemas.paginate_schema import PageMeta

from repositories.group_repositories import GroupRepository
from repositories.user_repository import UserRepository
from repositories.workout_repositories import WorkoutRepository
from services.base_services import BaseServices
from utils.context import get_current_user
from core.config import get_limits
from utils.raises import _forbidden, _not_found


class GroupServices(BaseServices):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.workout_repo = WorkoutRepository(session)
        self.repo = GroupRepository(session)
        self.user_repo = UserRepository(session)

    async def create_group(self, group_schema: GroupCreateSchema):
        self.log.info("create group")
        current_user = get_current_user()
        if await self.repo.get_groups_user_count(current_user.id) >= get_limits(current_user.plan).groups_limit:
            raise _forbidden("You have reached the limit for creating groups.")
        return await self.repo.add_group(group_schema.model_dump(), current_user.id)

    async def rename_group(self, group_id: int, group_name: str) -> GroupModel:
        self.log.info("rename group")
        current_user = get_current_user()
        group = await self.repo.get_group_by_id(group_id, current_user.id)
        if group is None:
            raise _not_found("Not found group for you")
        await self.repo.rename_group(group_name, group_id)
        return await self.repo.get_group_by_id(group_id, current_user.id)

    async def delete_group(self, group_id: int):
        self.log.info("delete group")
        current_user = get_current_user()
        group = await self.repo.get_group_by_id(group_id, current_user.id)
        if group is None:
            raise _forbidden("Not found group for you")
        await self.repo.delete_group(group_id, current_user.id)
        return group

    async def add_members_in_group(self, id_group: int, members_schema: List[GroupMembersAddSchema]):
        self.log.info("add members in group")
        current_user = get_current_user()
        list_members_id = {member.user_id for member in members_schema}
        group = await self.repo.get_group_by_id_with_full_relation(id_group, current_user.id)
        if group is None:
            raise _forbidden("Not found group for you")
        if len(group.members) >= get_limits(current_user.plan).members_group_limit:
            raise _forbidden("You cannot add more users to this group")
        if list_members_id & {member.id for member in group.members if member is not None}:
            raise _forbidden(
                f"you are trying to add users that are already in the list {[member.email for member in group.members]}")
        result = await self.user_repo.find_count_users_by_id(list(list_members_id))
        if len(list_members_id) != result:
            raise _forbidden("Not fount user in list")

        return await self.repo.add_members_group(list(list_members_id), id_group, current_user.id)

    async def get_groups_user(self, limit: int, start: int) -> GroupPage:
        self.log.info("get groups user")
        current_user = get_current_user()
        groups, total = await self.repo.get_groups_user(current_user.id, limit, start)
        pages = ceil(total / limit) if limit else 1
        return GroupPage(
            groups=groups,
            meta=PageMeta(total=total, limit=limit, pages=pages),
        )

    async def get_group_by_id(self, id_group: int) -> GroupModel:
        self.log.info("get group by id")
        current_user = get_current_user()
        group = await self.repo.get_group_by_id_with_full_relation(id_group, current_user.id)
        if group is None:
            raise _forbidden("Not found group")
        return group

    async def delete_members(self, members: List[GroupMembersAddSchema], group_id: int) -> GroupModel:
        self.log.info("delete members")
        current_user = get_current_user()
        group = await self.repo.get_group_by_id(group_id, current_user.id)
        if group is None:
            raise _forbidden("Not found group")
        ids_members = [member.user_id for member in members]
        await self.repo.remove_member_group_id(ids_members, group_id)
        return await self.repo.get_group_by_id_with_full_relation(group_id, current_user.id)

    async def delete_workout_from_group(self, group_id: int):
        self.log.info("delete workout from group")
        current_user = get_current_user()
        group = await self.repo.get_group_by_id(group_id, current_user.id)
        if group is None:
            raise _forbidden("Not found group")
        return await self.repo.remove_workout_from_group(group_id)

    async def add_workout_in_group(self, id_group: int, id_workout: int):
        self.log.info("add workout in group")
        current_user = get_current_user()
        workout = await self.workout_repo.get_workout_with_user(id_workout, current_user.id)
        if workout is None:
            raise _forbidden("Not found workout for you")
        group = await self.repo.get_group_by_id(id_group, current_user.id)
        if group is None:
            raise _forbidden("Not found group for you")

        return await self.repo.update_workout_in_group(id_group, id_workout, current_user.id)
