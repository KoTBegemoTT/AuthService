import pytest
from fastapi import HTTPException, status

from app.auth_service import views
from app.auth_service.views import (
    auth_view,
    create_and_put_token,
    found_user,
    get_username_by_token_view,
    hash_password,
    is_token_exist,
    is_token_expired,
    register_view,
    user_tokens,
    users,
    validate_auth_user,
    validate_token,
    verify_password,
)
from app.jwt_tokens.jwt_process import jwt_encode
from app.models import User
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
        return password == saved_password

    monkeypatch.setattr(views, 'verify_password', new_verify_password)


@pytest.fixture
def mock_hash_password(monkeypatch):
    def return_same_password(password):
        return password

    monkeypatch.setattr(views, 'hash_password', return_same_password)


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
async def test_register(
    mock_token, mock_hash_password, username, password,
):
    new_user = UserSchema(name=username, password=password)
    await register_view(new_user)

    assert len(users) == 1
    assert len(user_tokens) == 1
    user = users[0]
    token = user_tokens[user]

    assert user.name == username
    assert user.password == password
    assert token == mock_token


@pytest.mark.asyncio
async def test_register_many_users(mock_hash_password, mock_token):
    for i in range(10):
        new_user = UserSchema(name=f'user_{i}', password=f'password_{i}')
        await register_view(new_user)

    assert len(users) == 10
    assert len(user_tokens) == 10

    for i in range(10):
        user = users[i]
        token = user_tokens[user]

        assert user.name == f'user_{i}'
        assert user.password == f'password_{i}'
        assert token == mock_token


@pytest.mark.asyncio
async def test_found_user():
    assert await found_user('user_1') is None

    user = User('user_1', b'password_1')
    users.append(user)

    assert await found_user('user_1') == user


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
async def test_register_fail_user_exists(
        mock_hash_password, mock_token, username, password, second_password,
):
    with pytest.raises(HTTPException) as ex:
        await register_view(UserSchema(name=username, password=password))
        await register_view(UserSchema(
            name=username, password=second_password))

    assert ex.value.status_code == status.HTTP_409_CONFLICT
    assert ex.value.detail == 'Username already exists'


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
async def test_validate_auth_user_success(
    mock_verify_password, username, password,
):
    user = User(username, password)
    users.append(user)

    user_out = await validate_auth_user(
        UserSchema(name=username, password=password),
    )

    assert user_out == user


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
async def test_validate_auth_user_no_user(
    mock_verify_password, username, password,
):
    with pytest.raises(HTTPException) as ex:
        await validate_auth_user(UserSchema(name=username, password=password))

    assert ex.value.status_code == status.HTTP_403_FORBIDDEN
    assert ex.value.detail == 'Invalid username or password'


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
async def test_validate_auth_user_fail_wrong_password(
    mock_verify_password, username, password,
):
    user = User(username, password)
    users.append(user)

    with pytest.raises(HTTPException) as ex:
        await validate_auth_user(UserSchema(
            name=username, password='wrong_password',
        ))

    assert ex.value.status_code == status.HTTP_403_FORBIDDEN
    assert ex.value.detail == 'Invalid username or password'


@pytest.mark.parametrize('username, password', user_password_params)
@pytest.mark.asyncio
async def test_create_and_put_token(
        mock_verify_password, mock_token, username, password,
):
    user = User(username, password)
    users.append(user)

    token = await create_and_put_token(user)

    assert token == mock_token
    assert user_tokens[user] == token


@pytest.mark.asyncio
async def test_is_token_exist():
    user = User('user_1', b'password_1')
    assert not await is_token_exist(user)

    user_tokens[user] = 'token'
    assert await is_token_exist(user)


@pytest.mark.asyncio
@pytest.mark.parametrize('expire_minutes, is_expired', [
    pytest.param(0, True, id='expired_token'),
    pytest.param(10, False, id='not_expired_token'),
])
async def test_is_token_expired(expire_minutes, is_expired):
    user = User('user_1', b'password_1')
    token = jwt_encode(user=user, expire_minutes=expire_minutes)

    assert await is_token_expired(token) == is_expired


@pytest.mark.asyncio
@pytest.mark.parametrize('username, password', user_password_params)
async def test_auth_no_token(mock_token, username, password):
    user = User(username, password)
    token = await auth_view(user)
    assert token == mock_token


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'username, password, expire_minutes, is_token_old',
    [
        pytest.param('user_1', 'password_1', 0, False, id='expired_token'),
        pytest.param('user_1', 'password_1', 10, True, id='not_expired_token'),
    ])
async def test_auth_token(
    mock_token, username, password, expire_minutes, is_token_old,
):
    user = User(username, password)
    old_token = jwt_encode(user=user, expire_minutes=expire_minutes)
    user_tokens[user] = old_token

    token = await auth_view(user)

    assert user_tokens[user] == token
    assert (token == old_token) == is_token_old  # noqa: WPS309


@pytest.mark.asyncio
async def test_validate_token_success():
    user = User('user_1', b'password_1')
    token = jwt_encode(user)

    validated = validate_token(token)

    assert validated.get('username') == user.name


@pytest.mark.asyncio
async def test_validate_token_invalid():
    with pytest.raises(HTTPException) as ex:
        validate_token('invalid')

    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == 'invalid token'


@pytest.mark.asyncio
async def test_validate_token_expired():
    user = User('user_1', b'password_1')
    token = jwt_encode(user, expire_minutes=0)

    with pytest.raises(HTTPException) as ex:
        validate_token(token)

    assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert ex.value.detail == 'token expired'


@pytest.mark.asyncio
@pytest.mark.parametrize('username, password', user_password_params)
async def test_get_username_by_token(username, password):
    user = User(username, password)
    users.append(user)
    pyload = {'username': user.name}

    username = await get_username_by_token_view(pyload)

    assert username == user.name


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'pyload, status_code, detail',
    [
        pytest.param({}, status.HTTP_401_UNAUTHORIZED,
                     'No username in token', id='no_username'),
        pytest.param({'username': None}, status.HTTP_401_UNAUTHORIZED,
                     'username invalid', id='invalid'),
        pytest.param({'username': 'user_1'}, status.HTTP_404_NOT_FOUND,
                     'User not found', id='not_found'),
    ],
)
async def test_get_username_by_token_fail(pyload, status_code, detail):
    with pytest.raises(HTTPException) as ex:
        await get_username_by_token_view(pyload)

    assert ex.value.status_code == status_code
    assert ex.value.detail == detail
