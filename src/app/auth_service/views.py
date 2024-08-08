import asyncio
import bcrypt  # noqa: WPS202
import brotli
from aiokafka import AIOKafkaProducer
import aiofiles
from fastapi import Depends, HTTPException, UploadFile, status
from jwt import ExpiredSignatureError, InvalidTokenError

from app.auth_service.schemas import UserSchema
from app.jwt_tokens.jwt_process import jwt_decode, jwt_encode
from app.models import User

users: list[User] = []
user_tokens: dict[User, str] = {}


def hash_password(password: str) -> bytes:
    """Хеширование пароля."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def verify_password(password: str, hashed_password: bytes) -> bool:
    """Проверка пароля."""
    return bcrypt.checkpw(password.encode(), hashed_password)


async def found_user(username: str) -> User | None:
    """Проверка существования пользователя."""
    for user in users:
        if user.name == username:
            return user
    return None


async def create_and_put_token(user: User) -> str:
    """Создание токена."""
    token = jwt_encode(user)
    user_tokens[user] = token
    return token


async def register_view(user_in: UserSchema) -> str:
    """Регистрация пользователя."""
    if await found_user(user_in.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Username already exists',
        )

    hashed_password = hash_password(user_in.password)
    user = User(user_in.name, hashed_password)
    users.append(user)
    return await create_and_put_token(user)


async def validate_auth_user(user_in: UserSchema) -> User:
    """Валидация пользователя."""
    user_bd = await found_user(user_in.name)

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


async def is_token_exist(user: User) -> bool:
    """Проверка существования токена."""
    return user in user_tokens


async def auth_view(user: User) -> str:
    """Авторизация пользователя."""
    if not await is_token_exist(user):
        return await create_and_put_token(user)

    token = user_tokens[user]
    if await is_token_expired(token):
        return await create_and_put_token(user)

    return token


async def get_token(user_id: int):
    """Получение токена."""
    if len(users) <= user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Token not found',
        )

    user = users[user_id]
    if not await is_token_exist(user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Token not found',
        )

    return user_tokens[user]


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


def create_producer() -> AIOKafkaProducer:
    return AIOKafkaProducer(bootstrap_servers="kafka:9092")


async def compress(message: str) -> bytes:
    return brotli.compress(bytes(message, 'utf-8'))


async def verify_view(file: UploadFile) -> None:
    """Верификация пользователя."""
    try:
        file_path = f"/usr/photos/{file.filename}"
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
            compressed = await compress(file_path)
            await asyncio.wait_for(create_producer().send(
                "faces", compressed), timeout=10,
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
