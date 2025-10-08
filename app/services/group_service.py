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
from utils.raises import _forbidden


class GroupServices(BaseServices):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.workout_repo = WorkoutRepository(session)
        self.repo = GroupRepository(session)
        self.repo_user = UserRepository(session)

    async def create_group(self, group_schema: GroupCreateSchema, user_id: int | None, ):
        self.log.info("create group")
        user = await self.repo_user.find_user_id(BaseServices.check_permission(get_current_user(), user_id), False)
        user.check_reached_limit_group(await self.repo.get_groups_user_count(user.id))
        group_schema._user_id = user.id
        return await self.repo.create_one_obj_model(group_schema.model_dump())

    async def rename_group(self, group_id: int, group_name: str) -> GroupModel:
        self.log.info("rename group")
        group = await self.repo.find_group_by_id(group_id, get_current_user().id, get_current_user().is_admin)
        await self.repo.rename_group(group_name, group_id)
        return await self.repo.get_group_user_by_id(group_id, group.user_id)

    async def add_members_in_group(self, id_group: int, members_schema: List[GroupMembersAddSchema],
                                   user_id: int | None):
        self.log.info("add members in group")
        list_members_id = {member.user_id for member in members_schema}
        user = await self.repo_user.find_user_id(BaseServices.check_permission(get_current_user(), user_id), False)
        group = await self.repo.get_group_by_id_with_full_relation(id_group, user.id, get_current_user().is_admin)
        user.check_reached_limit_group(len(group.members))
        if list_members_id & {member.id for member in group.members if member is not None}:
            raise _forbidden(
                f"you are trying to add users that are already in the list {[member.email for member in group.members]}")
        if len(list_members_id) != await self.repo_user.find_count_users_by_id(list(list_members_id)):
            raise _forbidden("Not fount user in list")
        return await self.repo.add_members_group(list(list_members_id), id_group, group.user_id)

    async def add_workout_in_group(self, group_id: int, id_workout: int, user_id: int | None):
        self.log.info("add workout in group")
        user = await self.repo_user.find_user_id(BaseServices.check_permission(get_current_user(), user_id), False)
        await self.workout_repo.get_workout_for_user(id_workout, user.id, get_current_user().is_admin)
        await self.repo.find_group_by_id(group_id, user.id, get_current_user().is_admin)
        return await self.repo.update_workout_in_group(group_id, id_workout, user.id)

    async def get_groups_user(self, limit: int, start: int, user_id: int | None, ) -> GroupPage:
        self.log.info("get groups user")
        groups, total = await self.repo.get_groups_user(BaseServices.check_permission(get_current_user(), user_id),
                                                        limit, start)
        pages = ceil(total / limit) if limit else 1
        return GroupPage(
            groups=groups,
            meta=PageMeta(total=total, limit=limit, pages=pages),
        )

    async def get_group_by_id(self, id_group: int) -> GroupModel:
        self.log.info("get group by id")
        return await self.repo.get_group_by_id_with_full_relation(id_group, get_current_user().id,
                                                                  get_current_user().is_admin)

    async def delete_members(self, members: List[GroupMembersAddSchema], group_id: int) -> GroupModel:
        self.log.info("delete members")
        group = await self.repo.find_group_by_id(group_id, get_current_user().id, get_current_user().is_admin)
        ids_members = [member.user_id for member in members]
        await self.repo.remove_member_group_id(ids_members, group_id)
        return await self.repo.get_group_by_id_with_full_relation(group_id, group.user_id)

    async def delete_workout_from_group(self, group_id: int):
        self.log.info("delete workout from group")
        await self.repo.find_group_by_id(group_id, get_current_user().id, get_current_user().is_admin)
        return await self.repo.remove_workout_from_group(group_id)

    async def delete_group(self, group_id: int):
        self.log.info("delete group")
        group = await self.repo.find_group_by_id(group_id, get_current_user().id, get_current_user().is_admin)
        await self.repo.delete_group(group_id, group.user_id)
        return True
