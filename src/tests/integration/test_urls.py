import pytest
from fastapi import status

from app.auth_service.views import user_tokens, users, verify_password
from app.jwt_tokens.jwt_process import jwt_decode, jwt_encode
from app.db.models import User

user_password_params = [
    pytest.param('user_1', 'password', id='user_1'),
    pytest.param('admin', 'admin', id='username_equals_password'),
    pytest.param('', '', id='empty_username_and_password'),
]

valid_token = jwt_encode(
    User(name='user_1', password=b'password'), expire_minutes=1000)
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
    'exists_user, exists_tokens, status_code, response_json',
    [
        pytest.param(
            [User(name='user', password=b'password')],
            {User(name='user', password=b'password'): valid_token},
            status.HTTP_200_OK,
            None,
            id='user_and_tokens_exist',
        ),
        pytest.param(
            [User(name='user', password=b'password')],
            {User(name='user', password=b'password'): invalid_token},
            status.HTTP_401_UNAUTHORIZED,
            {'detail': 'invalid token'},
            id='token_invalid',
        ),
        pytest.param(
            [User(name='user', password=b'password')],
            {User(name='user', password=b'password'): expired_token},
            status.HTTP_401_UNAUTHORIZED,
            {'detail': 'token expired'},
            id='token_expired',
        ),
        pytest.param(
            [],
            {User(name='user', password=b'password'): 'token'},
            status.HTTP_404_NOT_FOUND,
            {'detail': 'Token not found'},
            id='no_user',
        ),
        pytest.param(
            [User(name='user', password=b'password')],
            {},
            status.HTTP_404_NOT_FOUND,
            {'detail': 'Token not found'},
            id='no_token',
        ),
        pytest.param(
            [],
            {},
            status.HTTP_404_NOT_FOUND,
            {'detail': 'Token not found'},
            id='no_user_and_token',
        ),
    ],
)
@pytest.mark.asyncio
async def test_check_token(
    ac, exists_user, exists_tokens, status_code, response_json,
):
    users.extend(exists_user)
    user_tokens.update(exists_tokens)

    response = await ac.get('/check_token/', params={'user_id': 0})

    assert response.status_code == status_code
    assert response.json() == response_json


@pytest.mark.asyncio
async def test_check_ready(ac):
    response = await ac.get('/healthz/ready/')

    assert response.status_code == status.HTTP_200_OK
