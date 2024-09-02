import pytest
from fastapi import status
from sqlalchemy import select

from app.auth_service.views import user_tokens, verify_password
from app.db.models import User
from app.jwt_tokens.jwt_process import jwt_decode, jwt_encode

user_password_params = [
    pytest.param('user_1', 'password', id='user_1'),
    pytest.param('admin', 'admin', id='username_equals_password'),
    pytest.param('', '', id='empty_username_and_password'),
]

valid_token = jwt_encode(
    User(name='user_1', password=b'password'),
    expire_minutes=1000,
)
expired_token = jwt_encode(
    User(name='user_1', password=b'password'),
    expire_minutes=0,
)
invalid_token = 'invalid_token'  # noqa: S105


async def get_users(session):
    db_request = select(User).order_by(User.id)
    result = await session.execute(db_request)
    users = result.scalars().all()
    return list(users)


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
@pytest.mark.usefixtures('reset_db')
async def test_register(ac, username, password, db_helper):
    response = await ac.post(
        '/register/', json={'name': username, 'password': password})

    assert response.status_code == status.HTTP_201_CREATED

    async with db_helper.session_factory() as session:
        users = await get_users(session)

    assert len(users) == 1
    user = users[0]

    assert user.name == username
    assert verify_password(password, user.password)


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
@pytest.mark.usefixtures('reset_db')
async def test_register_user_exists(ac, username, password):
    await ac.post(
        '/register/', json={'name': username, 'password': password})

    response = await ac.post(
        '/register/', json={'name': username, 'password': password})

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
@pytest.mark.usefixtures('reset_db')
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
@pytest.mark.usefixtures('reset_db')
async def test_auth_no_user(
    ac, username, password,
):
    response = await ac.post(
        '/auth/', json={'name': username, 'password': password})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Invalid username or password'}


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
@pytest.mark.usefixtures('reset_db')
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
            {1: valid_token},
            status.HTTP_200_OK,
            None,
            id='user_and_tokens_exist',
        ),
        pytest.param(
            [User(name='user', password=b'password')],
            {1: invalid_token},
            status.HTTP_401_UNAUTHORIZED,
            {'detail': 'invalid token'},
            id='token_invalid',
        ),
        pytest.param(
            [User(name='user', password=b'password')],
            {1: expired_token},
            status.HTTP_401_UNAUTHORIZED,
            {'detail': 'token expired'},
            id='token_expired',
        ),
        pytest.param(
            [],
            {1: 'token'},
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
@pytest.mark.usefixtures('reset_db', 'clear_tokens')
@pytest.mark.asyncio
async def test_check_token(
    ac, exists_user, exists_tokens, status_code, response_json, db_helper,
):
    async with db_helper.session_factory() as session:
        for user in exists_user:
            session.add(user)
            await session.commit()
    user_tokens.update(exists_tokens)

    response = await ac.get('/check_token/', params={'user_id': 1})

    assert response.status_code == status_code
    assert response.json() == response_json


@pytest.mark.asyncio
async def test_check_ready(ac):
    response = await ac.get('/healthz/ready/')

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_metrics(ac):
    response = await ac.get('/metrics/')
    help_string = '# HELP auth_request_count_total Total number of requests'

    assert response.status_code == status.HTTP_200_OK
    assert help_string in response.text
