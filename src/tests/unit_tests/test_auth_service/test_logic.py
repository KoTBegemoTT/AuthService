import pytest

from app import logic
from app.logic import AuthService, users
from app.models import User

user_password_params = [
    pytest.param('user_1', 'password', id='user_1'),
    pytest.param('admin', 'admin', id='username_equals_password'),
    pytest.param('', '', id='empty_username_and_password'),
]


@pytest.fixture
def mock_token(monkeypatch):
    monkeypatch.setattr(logic, 'jwt_encode', lambda _: 'token')
    return 'token'


class TestAuthService:
    @pytest.mark.parametrize('username, password', user_password_params)
    def test_register(self, mock_token, username, password):
        AuthService.register(username, password)

        assert len(users) == 1
        user = list(users.keys())[0]

        assert user.username == username
        assert user.password == password
        assert users[user] == mock_token

    def test_register_many_users(self):
        for i in range(10):
            AuthService.register(f'user_{i}', f'password_{i}')

        assert len(users) == 10

    def test_user_exists(self):
        assert AuthService.user_exists('user_1') is False
        AuthService.register('user_1', 'password')
        assert AuthService.user_exists('user_1') is True

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
            self, username, password, second_password,):
        with pytest.raises(ValueError):
            AuthService.register(username, password)
            AuthService.register(username, second_password)

    @pytest.mark.parametrize('username, password', user_password_params)
    def test_login_success(self, mock_token, username, password):
        useer = User(username, password)
        users[useer] = 'some_token'

        token = AuthService.login(username, password)

        assert token == mock_token

    @pytest.mark.parametrize('username, password', user_password_params)
    def test_login_fail(self, username, password):
        token = AuthService.login(username, password)

        assert token is None
