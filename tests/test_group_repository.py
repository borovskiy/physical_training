import pytest
from db.models import GroupModel, UserModel
from repositories.group_repository import GroupRepository


@pytest.mark.asyncio
class TestGroupRepository:
    async def test_create_and_get_group(self, session):
        repo = GroupRepository(session)

        user = UserModel(email="grouptest@example.com", password_hash="123")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        group = GroupModel(name="Leg Day", user_id=user.id)
        session.add(group)
        await session.commit()
        await session.refresh(group)

        found = await repo.get_group_user_by_id(group.id, user.id)
        assert found.id == group.id
        assert found.user_id == user.id

    async def test_check_group_exists(self, session):
        repo = GroupRepository(session)

        user = UserModel(email="exists@example.com", password_hash="123")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        group = GroupModel(name="Chest", user_id=user.id)
        session.add(group)
        await session.commit()

        assert await repo.find_group_by_id(group.id, user.id) is True
        assert await repo.find_group_by_id(999, user.id) is False

    async def test_rename_and_delete_group(self, session):
        repo = GroupRepository(session)

        user = UserModel(email="rename@example.com", password_hash="123")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        group = GroupModel(name="Old", user_id=user.id)
        session.add(group)
        await session.commit()
        await session.refresh(group)

        await repo.rename_group("NewName", group.id)
        updated = await repo.get_group_user_by_id(group.id, user.id)
        assert updated.name == "NewName"

        await repo.delete_group(group.id, user.id)
        result = await repo.get_group_user_by_id(group.id, user.id)
        assert result is None
