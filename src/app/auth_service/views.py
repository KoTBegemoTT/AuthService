import bcrypt  # noqa: WPS202
from fastapi import Depends, HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError
from opentracing import global_tracer
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_service.schemas import UserSchema
from app.db.db_helper import db_helper
from app.db.models import User
from app.external.redis_client import RedisClient, get_redis_client
from app.jwt_tokens.jwt_process import jwt_decode, jwt_encode


def hash_password(password: str) -> bytes:
    """Хеширование пароля."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def verify_password(password: str, hashed_password: bytes) -> bool:
    """Проверка пароля."""
    return bcrypt.checkpw(password.encode(), hashed_password)


async def found_user(username: str, session: AsyncSession) -> User | None:
    """Получение пользователя по имени."""
    with global_tracer().start_active_span('found_user'):
        db_request = select(User).where(User.name == username)
        founded_user: Result = await session.execute(db_request)
        return founded_user.scalar()


async def create_and_put_token(user: User, redis_client: RedisClient) -> str:
    """Создание токена."""
    token = jwt_encode(user)
    redis_client.set_token(token, user.id)
    return token


async def register_view(
    user_in: UserSchema,
    redis_client: RedisClient,
    session: AsyncSession,
) -> str:
    """Регистрация пользователя."""
    with global_tracer().start_active_span('register_view') as scope:
        scope.span.set_tag('user_data', str(user_in))
        if await found_user(user_in.name, session):
            scope.span.set_tag('error', 'User already exists')
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Username already exists',
            )

        hashed_password = hash_password(user_in.password)

        user = User(name=user_in.name, password=hashed_password)
        session.add(user)
        await session.commit()
        return await create_and_put_token(user, redis_client)


async def validate_auth_user(
    user_in: UserSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> User:
    """Валидация пользователя."""
    with global_tracer().start_active_span('validate_auth_user') as scope:
        scope.span.set_tag('user_data', str(user_in))
        user_bd = await found_user(user_in.name, session)

        if user_bd is None:
            scope.span.set_tag('error', 'User not found')
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid username or password',
            )

        if not verify_password(user_in.password, user_bd.password):
            scope.span.set_tag('error', 'Wrong password')
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


async def auth_view(user: User, redis_client: RedisClient) -> str:
    """Авторизация пользователя."""
    with global_tracer().start_active_span('auth_view') as scope:
        scope.span.set_tag('user_id', str(user.id))
        cashed_token = redis_client.get_token(user.id)
        if cashed_token is None:
            scope.span.set_tag('info', 'Token not found, creating new')
            return await create_and_put_token(user, redis_client)

        if await is_token_expired(cashed_token):
            scope.span.set_tag('info', 'Token expired, creating new')
            return await create_and_put_token(user, redis_client)

        scope.span.set_tag('info', 'Token from cash healthy')
        return cashed_token


async def get_token(
    user_id: int,
    redis_client: RedisClient = Depends(get_redis_client),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """Получение токена."""
    with global_tracer().start_active_span('get_token') as scope:
        user = await session.get(User, user_id)
        if not user:
            scope.span.set_tag('error', 'User not found')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Token not found',
            )
        cashed_token = redis_client.get_token(user_id)

        if cashed_token is None:
            scope.span.set_tag('error', 'Token not found')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Token not found',
            )

        return cashed_token


async def validate_token(token: str = Depends(get_token)) -> None:
    """Валидация токена."""
    with global_tracer().start_active_span('validate_token') as scope:
        try:
            jwt_decode(token)
        except ExpiredSignatureError:
            scope.span.set_tag('error', 'token expired')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='token expired',
            )
        except InvalidTokenError:
            scope.span.set_tag('error', 'invalid token')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token',
            )
