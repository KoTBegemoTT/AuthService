import pytest

from app.auth_service.views import verify_password, users
from app.schemas import CreateUserSchema
from app.jwt_tokens.jwt_process import jwt_decode

user_password_params = [
    pytest.param('user_1', 'password', id='user_1'),
    pytest.param('admin', 'admin', id='username_equals_password'),
    pytest.param('', '', id='empty_username_and_password'),
]


class TestAuthService:
    @pytest.mark.parametrize('username, password', user_password_params)
    def test_register(self, test_client, username, password):
        response = test_client.post(
            '/users/register', json={'name': username, 'password': password})

        assert response.status_code == 201
        assert len(users) == 1
        user = list(users.keys())[0]

        assert user.name == username
        assert verify_password(password, user.password)

    @pytest.mark.parametrize('username, password', user_password_params)
    def test_login(self, test_client, username, password):
        test_client.post(
            '/users/register', json={'name': username, 'password': password})

        response = test_client.post(
            '/users/auth', json={'name': username, 'password': password})

        assert response.status_code == 201
        token = response.json()['token']

        assert token is not None
        decoded_token = jwt_decode(token)
        assert decoded_token['name'] == username
