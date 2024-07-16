import pytest

from src.app.auth_service import logic
from src.app.auth_service.logic import AuthService

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
        token = AuthService.login(username, password)

        assert token == mock_token
