from enum import nonmember
from typing import List, Sequence, Any

from sqlalchemy import select, func, and_, delete, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from db.models import GroupModel, GroupMemberModel
from repositories.base_repositoriey import BaseRepo


class GroupRepository(BaseRepo):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model_group = GroupModel
        self.model_member_group = GroupMemberModel

    async def add_group(self, data: dict, user_id: int) -> GroupModel:
        obj = self.model_group(**data)
        obj.user_id = user_id
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def rename_group(self, group_name: str, group_id: int):
        stmt = update(self.model_group).where(self.model_group.id == group_id).values(
            name=group_name)

        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_group(self, group_id: int, user_id: int) -> None:
        stmt = (
            delete(self.model_group)
            .where(
                self.model_group.id == group_id,
                self.model_group.user_id == user_id
            )
        )
        await self.remove_all_member_group_id(group_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def add_members_group(self, members_schema: List[int], id_group: int, user_id: int) -> GroupModel:
        list_members = []
        for member_id in members_schema:
            members_obj = GroupMemberModel(user_id=member_id, group_id=id_group)
            self.session.add(members_obj)
            list_members.append(members_obj)
        await self.session.commit()
        return await self.get_group_by_id_with_full_relation(id_group, user_id)

    async def get_group_by_id(self, id_group: int, user_id: int) -> GroupModel:
        stmt = (
            select(self.model_group)
            .where(
                and_(
                    self.model_group.id == id_group,
                    self.model_group.user_id == user_id
                ))
        )
        return await self.session.scalar(stmt)

    async def get_group_by_id_with_full_relation(self, id_group: int, user_id: int) -> GroupModel:
        stmt = (
            select(self.model_group).options(joinedload(self.model_group.members)).options(
                joinedload(self.model_group.workout))
            .where(
                and_(
                    self.model_group.id == id_group,
                    self.model_group.user_id == user_id
                ))
        )
        return await self.session.scalar(stmt)

    async def get_groups_user(self, user_id: int, limit: int, start: int) -> tuple[Sequence[GroupModel], Any]:
        base_where = (self.model_group.user_id == user_id,)
        stmt_group = (
            select(self.model_group)
            .where(*base_where)
            .order_by(self.model_group.created_at.asc())
            .offset(start * limit)
            .limit(limit)
        )
        groups_result = await self.session.scalars(stmt_group)
        groups = groups_result.all()

        stmt_count = select(func.count()).select_from(self.model_group).where(*base_where)
        total = await self.session.scalar(stmt_count)

        return groups, int(total)

    async def get_users_in_group_by_id(self, list_users_id: List[int], group_id: int) -> List[GroupMemberModel] | None:
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
        stmt = (
            select(func.count())
            .select_from(self.model_member_group)
            .where(self.model_member_group.group_id == group_id)
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def get_all_groups(self, user_id: int, limit: int, start: int):
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
        stmt = (
            delete(self.model_member_group)
            .where(
                self.model_member_group.group_id == group_id,
                self.model_member_group.user_id.in_(list_ids_members)
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def remove_all_member_group_id(self, group_id: int) -> None:
        stmt = (
            delete(self.model_member_group)
            .where(
                self.model_member_group.group_id == group_id,
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_workout_in_group(self, id_group: int, id_workout: int, user_id: int) -> GroupModel:
        stmt = update(self.model_group).where(self.model_group.id == id_group,
                                              self.model_group.user_id == user_id).values(workout_id=id_workout)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_group_by_id_with_full_relation(id_group, user_id)

    async def remove_workout_from_group(self, id_group: int) -> None:
        stmt = (
            update(self.model_member_group)
            .where(
                self.model_member_group.group_id == id_group,
            ).values(workout_id=None)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return None
