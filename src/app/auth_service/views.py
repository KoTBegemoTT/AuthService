import bcrypt  # noqa: WPS202
from fastapi import Depends, HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_service.schemas import UserSchema
from app.db.db_helper import db_helper
from app.db.models import User
from app.jwt_tokens.jwt_process import jwt_decode, jwt_encode

user_tokens: dict[int, str] = {}


def hash_password(password: str) -> bytes:
    """Хеширование пароля."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def verify_password(password: str, hashed_password: bytes) -> bool:
    """Проверка пароля."""
    return bcrypt.checkpw(password.encode(), hashed_password)


async def found_user(username: str, session: AsyncSession) -> User | None:
    """Получение пользователя по имени."""
    db_request = select(User).where(User.name == username)
    founded_user: Result = await session.execute(db_request)
    return founded_user.scalar()


async def create_and_put_token(user: User) -> str:
    """Создание токена."""
    token = jwt_encode(user)
    user_tokens[user.id] = token
    return token


async def register_view(
    user_in: UserSchema,
    session: AsyncSession,
) -> str:
    """Регистрация пользователя."""
    if await found_user(user_in.name, session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Username already exists',
        )

    hashed_password = hash_password(user_in.password)

    user = User(name=user_in.name, password=hashed_password)
    session.add(user)
    await session.commit()
    return await create_and_put_token(user)


async def validate_auth_user(
    user_in: UserSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> User:
    """Валидация пользователя."""
    user_bd = await found_user(user_in.name, session)

    if user_bd is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid username or password',
        )

    if not verify_password(user_in.password, user_bd.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid username or password',
        )

    return user_bd


async def is_token_expired(token: str) -> bool:
    """Проверка истечения срока действия токена."""
    try:
        jwt_decode(token)
    except ExpiredSignatureError:
        return True
    return False


async def is_token_exist(user_id: int) -> bool:
    """Проверка существования токена."""
    return user_id in user_tokens


async def auth_view(user: User) -> str:
    """Авторизация пользователя."""
    if not await is_token_exist(user.id):
        return await create_and_put_token(user)

    token = user_tokens[user.id]
    if await is_token_expired(token):
        return await create_and_put_token(user)

    return token


async def get_token(
    user_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """Получение токена."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Token not found',
        )

    if not await is_token_exist(user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Token not found',
        )

    return user_tokens[user.id]


async def validate_token(token: str = Depends(get_token)) -> None:
    """Валидация токена."""
    try:
        jwt_decode(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='token expired',
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid token',
        )
