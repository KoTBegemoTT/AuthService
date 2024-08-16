import pytest
from fastapi import HTTPException, status
from sqlalchemy import select

from app.auth_service import views
from app.auth_service.views import (
    auth_view,
    create_and_put_token,
    found_user,
    get_token,
    hash_password,
    is_token_exist,
    is_token_expired,
    register_view,
    user_tokens,
    validate_auth_user,
    validate_token,
    verify_password,
)
from app.db.models import User
from app.jwt_tokens.jwt_process import jwt_encode
from src.app.auth_service.schemas import UserSchema

user_password_params = [
    pytest.param('user_1', 'password', id='user_1'),
    pytest.param('admin', 'admin', id='username_equals_password'),
    pytest.param('', '', id='empty_username_and_password'),
]


@pytest.fixture
def mock_token(monkeypatch):
    monkeypatch.setattr(views, 'jwt_encode', lambda _: 'mocked_token')
    return 'mocked_token'


@pytest.fixture
def mock_verify_password(monkeypatch):
    def new_verify_password(password, saved_password):
        return bytes(password, 'utf-8') == saved_password

    monkeypatch.setattr(views, 'verify_password', new_verify_password)


@pytest.fixture
def mock_hash_password(monkeypatch):
    def get_password_in_bytes(password):
        return bytes(password, 'utf-8')

    monkeypatch.setattr(views, 'hash_password', get_password_in_bytes)


async def get_users(session):
    db_request = select(User).order_by(User.id)
    result = await session.execute(db_request)
    users = result.scalars().all()
    return list(users)


@pytest.mark.parametrize('password, confirm_password, is_verified', [
    pytest.param('password', 'password', True, id='same_password'),
    pytest.param('password', 'wrong_password', False, id='wrong_password'),
    pytest.param('sdf231#&*!', 'sdf231#&*!', True, id='strong_password'),
])
@pytest.mark.asyncio
async def test_hash_and_verify_password(
    password, confirm_password, is_verified,
):
    hashed_password = hash_password(password)

    assert verify_password(confirm_password, hashed_password) == is_verified


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_hash_password', 'reset_db', 'clear_tokens')
async def test_register(
    mock_token, db_helper, username, password,
):
    new_user = UserSchema(name=username, password=password)

    async with db_helper.session_factory() as session:
        await register_view(new_user, session)
        users = await get_users(session)

    assert len(users) == 1
    assert len(user_tokens) == 1
    user = users[0]
    token = user_tokens[user.id]

    assert user.name == username
    assert user.password == bytes(password, 'utf-8')
    assert token == mock_token


@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_hash_password', 'reset_db', 'clear_tokens')
async def test_register_many_users(mock_token, db_helper):
    async with db_helper.session_factory() as session:
        for i in range(10):
            new_user = UserSchema(name=f'user_{i}', password=f'password_{i}')
            await register_view(new_user, session)
        users = await get_users(session)

    assert len(users) == 10
    assert len(user_tokens) == 10

    for i in range(10):
        user = users[i]
        token = user_tokens[user.id]

        assert user.name == f'user_{i}'
        assert user.password == bytes(f'password_{i}', 'utf-8')
        assert token == mock_token


@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_hash_password', 'reset_db', 'clear_tokens')
async def test_found_user(db_helper):
    async with db_helper.session_factory() as session:
        assert await found_user('user_1', session) is None

        user = User(name='user_1', password=b'password_1')
        session.add(user)
        await session.commit()

        assert await found_user('user_1', session) == user


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
@pytest.mark.asyncio
@pytest.mark.usefixtures(
    'mock_hash_password', 'reset_db', 'clear_tokens', 'mock_token',
)
async def test_register_fail_user_exists(
        db_helper, username, password, second_password,
):
    async with db_helper.session_factory() as session:
        with pytest.raises(HTTPException) as ex:
            await register_view(
                UserSchema(name=username, password=password),
                session,
            )
            await register_view(
                UserSchema(name=username, password=second_password),
                session,
            )

    assert ex.value.status_code == status.HTTP_409_CONFLICT
    assert ex.value.detail == 'Username already exists'


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
@pytest.mark.usefixtures('reset_db', 'mock_verify_password')
async def test_validate_auth_user_success(username, password, db_helper):
    user = User(name=username, password=bytes(password, 'utf-8'))
    async with db_helper.session_factory() as session:
        session.add(user)
        await session.commit()
        user_out = await validate_auth_user(
            UserSchema(name=username, password=password),
            session,
        )

    assert user_out == user


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
@pytest.mark.usefixtures('reset_db', 'mock_verify_password')
async def test_validate_auth_user_no_user(username, password, db_helper):
    async with db_helper.session_factory() as session:
        with pytest.raises(HTTPException) as ex:
            await validate_auth_user(
                UserSchema(name=username, password=password),
                session,
            )

    assert ex.value.status_code == status.HTTP_403_FORBIDDEN
    assert ex.value.detail == 'Invalid username or password'


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
@pytest.mark.usefixtures('reset_db', 'mock_verify_password')
async def test_validate_auth_user_fail_wrong_password(
    username, password, db_helper,
):
    user = User(name=username, password=bytes(password, 'utf-8'))
    async with db_helper.session_factory() as session:
        session.add(user)
        await session.commit()

        with pytest.raises(HTTPException) as ex:
            await validate_auth_user(
                UserSchema(name=username, password='wrong_password'),
                session,
            )

    assert ex.value.status_code == status.HTTP_403_FORBIDDEN
    assert ex.value.detail == 'Invalid username or password'


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.usefixtures('mock_verify_password', 'clear_tokens')
@pytest.mark.asyncio
async def test_create_and_put_token(
        mock_token, username, password, db_helper,
):
    user = User(name=username, password=bytes(password, 'utf-8'))

    token = await create_and_put_token(user)

    assert token == mock_token
    assert user_tokens[user.id] == token


@pytest.mark.asyncio
@pytest.mark.usefixtures('clear_tokens')
async def test_is_token_exist():
    user = User(name='user_1', password=b'password_1')
    assert not await is_token_exist(user.id)

    user_tokens[user.id] = 'token'
    assert await is_token_exist(user.id)


@pytest.mark.asyncio
@pytest.mark.parametrize('expire_minutes, is_expired', [
    pytest.param(0, True, id='expired_token'),
    pytest.param(10, False, id='not_expired_token'),
])
@pytest.mark.usefixtures('clear_tokens')
async def test_is_token_expired(expire_minutes, is_expired):
    user = User(name='user_1', password=b'password_1')
    token = jwt_encode(user=user, expire_minutes=expire_minutes)

    assert await is_token_expired(token) == is_expired


@pytest.mark.asyncio
@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.usefixtures('clear_tokens')
async def test_auth_no_token(mock_token, username, password):
    user = User(name=username, password=bytes(password, 'utf-8'))
    token = await auth_view(user)
    assert token == mock_token


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'username, password, expire_minutes, is_token_old',
    [
        pytest.param('user_1', 'password_1', 0, False, id='expired_token'),
        pytest.param('user_1', 'password_1', 10, True, id='not_expired_token'),
    ])
@pytest.mark.usefixtures('clear_tokens', 'mock_token')
async def test_auth_token(
    username, password, expire_minutes, is_token_old,
):
    user = User(name=username, password=bytes(password, 'utf-8'))
    old_token = jwt_encode(user=user, expire_minutes=expire_minutes)
    user_tokens[user.id] = old_token

    token = await auth_view(user)

    assert user_tokens[user.id] == token
    is_token_equal = (token == old_token)
    assert is_token_equal == is_token_old  # noqa: WPS309


@pytest.mark.asyncio
async def test_validate_token_success():
    user = User(name='user_1', password=b'password_1')
    token = jwt_encode(user)

    await validate_token(token)


@pytest.mark.asyncio
async def test_validate_token_invalid():
    with pytest.raises(HTTPException) as ex:
        await validate_token('invalid')

    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == 'invalid token'


@pytest.mark.asyncio
async def test_validate_token_expired():
    user = User(name='user_1', password=b'password_1')
    token = jwt_encode(user, expire_minutes=0)

    with pytest.raises(HTTPException) as ex:
        await validate_token(token)

    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == 'token expired'


@pytest.mark.asyncio
@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.usefixtures('clear_tokens', 'reset_db')
async def test_get_token(username, password, db_helper):
    user = User(name=username, password=bytes(password, 'utf-8'))
    async with db_helper.session_factory() as session:
        session.add(user)
        await session.commit()

        user_tokens[user.id] = 'token'

        token = await get_token(user_id=user.id, session=session)

    assert token == 'token'


@pytest.mark.asyncio
@pytest.mark.usefixtures('clear_tokens', 'reset_db')
async def test_get_token_no_user(db_helper):
    async with db_helper.session_factory() as session:
        with pytest.raises(HTTPException) as ex:
            await get_token(user_id=1, session=session)

    assert ex.value.status_code == status.HTTP_404_NOT_FOUND
    assert ex.value.detail == 'Token not found'


@pytest.mark.asyncio
@pytest.mark.usefixtures('clear_tokens', 'reset_db')
async def test_get_token_no_token(db_helper):
    user = User(name='user_1', password=b'password_1')
    async with db_helper.session_factory() as session:
        session.add(user)
        await session.commit()

        with pytest.raises(HTTPException) as ex:
            await get_token(user_id=user.id, session=session)

    assert ex.value.status_code == status.HTTP_404_NOT_FOUND
    assert ex.value.detail == 'Token not found'
