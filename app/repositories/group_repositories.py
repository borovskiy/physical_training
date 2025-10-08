from typing import List, Sequence, Any, Coroutine

from sqlalchemy import select, func, and_, delete, update, or_, Row, RowMapping, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from db.models import GroupModel, GroupMemberModel
from repositories.base_repositoriey import BaseRepo
from utils.raises import _not_found


class GroupRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = GroupModel
        self.model_member_group = GroupMemberModel

    async def get_group_user_by_id(self, id_group: int, user_id: int) -> GroupModel:
        self.log.info("get_group_by_id")
        stmt = (
            select(self.model)
            .where(
                and_(
                    self.model.id == id_group,
                    self.model.user_id == user_id
                ))
        )
        return await self.session.scalar(stmt)

    async def find_group_by_id(self, id_group: int, user_id: int, for_admin: bool = False) -> GroupModel:
        stmt = select(
            exists().where(
                and_(
                    self.model.id == id_group,
                    *([] if for_admin else [self.model.user_id == user_id])
                )
            )
        )
        group = await self.execute_session_get_first(stmt)
        if group is None:
            raise _not_found("Group not found")
        return group

    async def rename_group(self, group_name: str, group_id: int):
        self.log.info("rename_group")
        stmt = update(self.model).where(self.model.id == group_id).values(name=group_name)
        await self.execute_session_and_commit(stmt)

    async def delete_group(self, group_id: int, user_id: int) -> None:
        self.log.info("delete_group")
        stmt = (
            delete(self.model)
            .where(self.model.id == group_id, self.model.user_id == user_id)
        )
        await self.remove_all_member_group_id(group_id)
        await self.execute_session_and_commit(stmt)

    async def add_members_group(self, members_schema: List[int], id_group: int, user_id: int) -> GroupModel:
        self.log.info("add_members_group members_schema %s id_group %s user_id %s", members_schema, id_group, user_id)
        list_members = []
        for member_id in members_schema:
            members_obj = GroupMemberModel(user_id=member_id, group_id=id_group)
            self.session.add(members_obj)
            list_members.append(members_obj)
        await self.session.commit()
        return await self.get_group_by_id_with_full_relation(id_group, user_id)

    async def get_group_by_id_with_full_relation(self, id_group: int, user_id: int,
                                                 for_admin: bool = False) -> GroupModel:
        self.log.info("get_group_by_id_with_full_relation")
        stmt = (
            select(self.model)
            .options(joinedload(self.model.members))
            .options(joinedload(self.model.workout))
            .options(joinedload(self.model.user))
            .where(
                and_(
                    self.model.id == id_group,
                    *([] if for_admin else [self.model.user_id == user_id]))
            )
        )
        group = await self.execute_session_get_first(stmt)
        if group is None:
            raise _not_found("Group not found")
        return group

    async def get_groups_user(self, user_id: int, limit: int, start: int) -> tuple[Sequence[GroupModel], Any]:
        self.log.info("get_groups_user")
        base_where = (self.model.user_id == user_id,)
        stmt_group = (
            select(self.model)
            .where(*base_where)
            .order_by(self.model.created_at.asc())
            .offset(start * limit)
            .limit(limit)
        )
        groups_result = await self.session.scalars(stmt_group)
        groups = groups_result.all()

        stmt_count = select(func.count()).select_from(self.model).where(*base_where)
        total = await self.session.scalar(stmt_count)

        return groups, int(total)

    async def get_groups_user_count(self, user_id: int) -> int:
        self.log.info("get_groups_user_count")
        base_where = (self.model.user_id == user_id,)
        stmt_count = select(func.count()).select_from(self.model).where(*base_where)
        total = await self.session.scalar(stmt_count)
        return int(total)

    async def get_users_in_group_by_id(self, list_users_id: List[int], group_id: int) -> Sequence[GroupMemberModel]:
        self.log.info("get_users_in_group_by_id")
        stmt = (select(self.model_member_group)
        .options(selectinload(self.model_member_group.user))
        .where(
            and_(
                self.model_member_group.group_id == group_id,
                self.model_member_group.user_id.in_(list_users_id)
            )))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_users_count_in_group_by_id(self, group_id: int) -> int:
        self.log.info("get_users_count_in_group_by_id")
        stmt = (
            select(func.count())
            .select_from(self.model_member_group)
            .where(self.model_member_group.group_id == group_id)
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def get_all_groups(self, user_id: int, limit: int, start: int):
        self.log.info("get_all_groups")
        stmt_workouts = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.created_at.asc())
            .offset(limit * start)
            .limit(limit)
        )
        res_workouts = await self.session.execute(stmt_workouts)
        workouts = res_workouts.scalars().all()
        stmt_count_workouts = select(func.count()).select_from(
            select(self.model.id).where(self.model.user_id == user_id).subquery()
        )
        total = (await self.session.execute(stmt_count_workouts)).scalar_one()
        return workouts, total

    async def remove_member_group_id(self, list_ids_members: List[int], group_id: int) -> None:
        self.log.info("remove_member_group_id")
        stmt = (
            delete(self.model_member_group)
            .where(
                self.model_member_group.group_id == group_id,
                self.model_member_group.user_id.in_(list_ids_members)
            )
        )
        await self.execute_session_and_commit(stmt)

    async def remove_all_member_group_id(self, group_id: int) -> None:
        self.log.info("remove_all_member_group_id")
        stmt = (
            delete(self.model_member_group)
            .where(
                self.model_member_group.group_id == group_id,
            )
        )
        await self.execute_session_and_commit(stmt)

    async def update_workout_in_group(self, id_group: int, id_workout: int, user_id: int) -> GroupModel:
        self.log.info("update_workout_in_group")
        stmt = update(self.model).where(self.model.id == id_group,
                                        self.model.user_id == user_id).values(workout_id=id_workout)
        await self.execute_session_and_commit(stmt)

        return await self.get_group_by_id_with_full_relation(id_group, user_id)

    async def remove_workout_from_group(self, id_group: int) -> None:
        self.log.info("remove_workout_from_group")
        stmt = (
            update(self.model)
            .where(
                self.model.id == id_group,
            ).values(workout_id=None)
        )
        await self.execute_session_and_commit(stmt)

        return None
