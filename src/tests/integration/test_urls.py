import pytest
from fastapi import status

from app.auth_service.views import users, verify_password
from app.jwt_tokens.jwt_process import jwt_decode, jwt_encode
from app.models import User

user_password_params = [
    pytest.param('user_1', 'password', id='user_1'),
    pytest.param('admin', 'admin', id='username_equals_password'),
    pytest.param('', '', id='empty_username_and_password'),
]

expired_token = jwt_encode(
    User(name='user_1', password=b'password'), expire_minutes=0)
invalid_token = 'invalid_token'  # noqa: S105


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
async def test_register(ac, username, password):
    response = await ac.post(
        '/register/', json={'name': username, 'password': password})

    assert response.status_code == status.HTTP_201_CREATED
    assert len(users) == 1
    user = users[0]

    assert user.name == username
    assert verify_password(password, user.password)


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
async def test_register_user_exists(ac, username, password):
    await ac.post(
        '/register/', json={'name': username, 'password': password})

    response = await ac.post(
        '/register/', json={'name': username, 'password': password})

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
async def test_auth(ac, username, password):
    await ac.post(
        '/register/', json={'name': username, 'password': password})

    response = await ac.post(
        '/auth/', json={'name': username, 'password': password})

    assert response.status_code == status.HTTP_201_CREATED
    token = response.json()

    decoded_token = jwt_decode(token)
    assert decoded_token['username'] == username


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
async def test_auth_no_user(
    ac, username, password,
):
    response = await ac.post(
        '/auth/', json={'name': username, 'password': password})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Invalid username or password'}


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
async def test_auth_wrong_password(
    ac, username, password,
):
    await ac.post(
        '/register/', json={'name': username, 'password': password})

    response = await ac.post(
        '/auth/', json={'name': username, 'password': 'wrong_password'})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Invalid username or password'}


@pytest.mark.parametrize(
    'token, detail',
    [
        pytest.param(expired_token, 'token expired', id='expired'),
        pytest.param(invalid_token, 'invalid token', id='invalid'),
    ],
)
@pytest.mark.asyncio
async def test_check_token_invalid(ac, token, detail):
    response = await ac.get('/check_token/', params={'token': token})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': detail}


@pytest.mark.parametrize(
    'exists_user, status_code, response_json',
    [
        pytest.param([User(name='user', password=b'password')],
                     status.HTTP_200_OK, 'user', id='user_exists'),
        pytest.param([], status.HTTP_404_NOT_FOUND,
                     {'detail': 'User not found'}, id='user_not_found'),
    ],
)
@pytest.mark.asyncio
async def test_check_token(ac, exists_user, status_code, response_json):
    users.extend(exists_user)

    token = jwt_encode(User(name='user', password=b'password'))
    response = await ac.get('/check_token/', params={'token': token})

    assert response.status_code == status_code
    assert response.json() == response_json
