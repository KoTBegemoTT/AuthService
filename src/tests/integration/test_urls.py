import pytest
from fastapi import status

from app.auth_service.views import users, verify_password
from app.jwt_tokens.jwt_process import jwt_decode

user_password_params = [
    pytest.param('user_1', 'password', id='user_1'),
    pytest.param('admin', 'admin', id='username_equals_password'),
    pytest.param('', '', id='empty_username_and_password'),
]


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
async def test_register(ac, username, password):
    response = await ac.post(
        '/register/', json={'name': username, 'password': password})

    assert response.status_code == status.HTTP_201_CREATED
    assert len(users) == 1
    user = list(users.keys())[0]

    assert user.name == username
    assert verify_password(password, user.password)


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
async def test_login(ac, username, password):
    await ac.post(
        '/register/', json={'name': username, 'password': password})

    response = await ac.post(
        '/auth/', json={'name': username, 'password': password})

    assert response.status_code == status.HTTP_201_CREATED
    token = response.json()['token']

    assert token is not None
    decoded_token = jwt_decode(token)
    assert decoded_token['name'] == username
