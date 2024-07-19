import pytest

from app.models import User
from app.auth_service import views
from app.auth_service.views import register_view, login_view, user_exists, hash_password, users
from app.schemas import CreateUserSchema, LoginUserSchema

user_password_params = [
    pytest.param("user_1", "password", id="user_1"),
    pytest.param("admin", "admin", id="username_equals_password"),
    pytest.param("", "", id="empty_username_and_password"),
]


@pytest.fixture
def mock_token(monkeypatch):
    monkeypatch.setattr(views, "jwt_encode", lambda _: "token")
    return "token"


@pytest.fixture
def mock_verify_password(monkeypatch):
    def new_verify_password(password, saved_password):
        return password == saved_password

    monkeypatch.setattr(views, "verify_password", new_verify_password)


@pytest.fixture
def mock_hash_password(monkeypatch):
    def return_same_password(password):
        return password

    monkeypatch.setattr(views, "hash_password", return_same_password)


class TestAuthService:
    @pytest.mark.parametrize("username, password", user_password_params)
    def test_register(self, mock_token, mock_hash_password, username, password):
        new_user = CreateUserSchema(name=username, password=password)
        register_view(new_user)

        assert len(users) == 1
        user = list(users.keys())[0]

        assert user.name == username
        assert user.password == password
        assert users[user] == mock_token

    def test_register_many_users(self, mock_hash_password, mock_token):
        for i in range(10):
            new_user = CreateUserSchema(
                name=f"user_{i}", password=f"password_{i}")
            register_view(new_user)

        assert len(users) == 10

    def test_user_exists(self, mock_token):
        assert user_exists('user_1') is False
        user = User('user_1', b'password_1')
        users[user] = 'token'
        assert user_exists('user_1') is True

    @pytest.mark.parametrize(
        'username, password, second_password',
        [
            pytest.param('user_1', 'password', 'other_password',
                         id='different_password',),
            pytest.param('user_1', 'user_1', 'user_1', id='same_password'),
            pytest.param('', '', 'other_password',
                         id='empty_username_and_password',),
        ],
    )
    def test_register_fail_user_exists(
            self, mock_hash_password, mock_token,
            username, password, second_password,
    ):
        with pytest.raises(ValueError):
            register_view(CreateUserSchema(name=username, password=password))
            register_view(CreateUserSchema(
                name=username, password=second_password))

    @pytest.mark.parametrize('username, password', user_password_params)
    def test_login_success(
            self, monkeypatch, mock_verify_password,
            mock_token, username, password,
    ):
        user = User(username, password)
        users[user] = 'some_token'

        token = login_view(LoginUserSchema(name=username, password=password))

        assert token == mock_token

    @pytest.mark.parametrize('username, password', user_password_params)
    def test_login_fail_no_user(self, mock_verify_password, username, password):
        token = login_view(LoginUserSchema(name=username, password=password))

        assert token is None

    @pytest.mark.parametrize('username, password', user_password_params)
    def test_login_fail_wrong_password(
        self, mock_verify_password,
        username, password
    ):
        user = User(username, password)
        users[user] = 'some_token'

        token = login_view(
            LoginUserSchema(name=username, password='wrong_password'))

        assert token is None
