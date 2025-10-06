import pytest
from db.models.user_model import UserModel
from repositories.user_repository import UserRepository


@pytest.mark.asyncio
class TestUserRepository:
    """
    Класс для тестирования методов UserRepository.
    Все тесты внутри работают асинхронно и используют фикстуру user_repo.
    """

    @pytest.mark.asyncio
    async def test_add_and_find_user(self, user_repo: UserRepository):
        """
        Проверяем добавление пользователя и поиск по email.
        """
        user = UserModel(email="test@example.com", password_hash="hash123")
        user_repo.session.add(user)
        await user_repo.session.commit()
        await user_repo.session.refresh(user)
        found = await user_repo.find_user_email("test@example.com")
        assert found is not None
        assert found.email == "test@example.com"

    async def test_find_user_id(self, user_repo: UserRepository):
        """
        Проверяем поиск пользователя по ID.
        """
        user = UserModel(email="id_user@example.com", password_hash="hash123")
        user_repo.session.add(user)
        await user_repo.session.commit()
        await user_repo.session.refresh(user)

        found = await user_repo.find_user_id(user.id)

        assert found.id == user.id

    async def test_update_user(self, user_repo: UserRepository):
        """
        Проверяем обновление данных пользователя.
        """
        user = UserModel(email="update@example.com", password_hash="hash123")
        user_repo.session.add(user)
        await user_repo.session.commit()
        await user_repo.session.refresh(user)

        updated = await user_repo.update_user({"first_name": "John"}, user.id)
        assert updated.first_name == "John"

    async def test_add_token_user(self, user_repo: UserRepository):
        """
        Проверяем добавление токена пользователю.
        """
        user = UserModel(email="token@example.com", password_hash="hash123")
        user_repo.session.add(user)
        await user_repo.session.commit()
        await user_repo.session.refresh(user)

        token = await user_repo.add_token_user("sometoken", user.id)
        assert token == "sometoken"

        found = await user_repo.find_user_id(user.id, need_token=True)
        assert found.token.token == "sometoken"

    async def test_update_token_user(self, user_repo: UserRepository):
        """
        Проверяем обновление токена пользователя.
        """
        user = UserModel(email="update_token@example.com", password_hash="hash123")
        user_repo.session.add(user)
        await user_repo.session.commit()
        await user_repo.session.refresh(user)

        await user_repo.add_token_user("oldtoken", user.id)
        new_token = await user_repo.update_token_user("newtoken", user.id)

        assert new_token == "newtoken"

    async def test_remove_user_id(self, user_repo: UserRepository):
        """
        Проверяем удаление пользователя по ID.
        """
        user = UserModel(email="remove@example.com", password_hash="hash123")
        user_repo.session.add(user)
        await user_repo.session.commit()
        await user_repo.session.refresh(user)

        result = await user_repo.remove_user_id(user.id)
        assert result is True
