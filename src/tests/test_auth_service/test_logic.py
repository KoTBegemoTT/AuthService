import pytest
from app.logic import AuthService, users


class TestAuthService:
    def test_register(self):
        AuthService.register("user_1", "password")

        assert len(users) == 1
        user = list(users.keys())[0]

        assert user.username == "user_1"
        assert user.password == "password"
        assert users[user] is not None

    def test_user_exists(self):
        assert AuthService.user_exists("user_1") is False
        AuthService.register("user_1", "password")
        assert AuthService.user_exists("user_1") is True

    def test_register_fail(self):
        with pytest.raises(ValueError):
            AuthService.register("user_1", "password")
            AuthService.register("user_1", "other_password")

    def test_login_success(self, add_user_1):
        token = AuthService.login("user_1", "password")

        assert token is not None

    def test_login_fail(self):
        token = AuthService.login("user_1", "password")

        assert token is None
