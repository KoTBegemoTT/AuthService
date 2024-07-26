from dataclasses import asdict

import bcrypt

from app.jwt_tokens.jwt_process import jwt_encode
from app.models import User
from app.auth_service.schemas import UserSchema

users: dict[User, str] = {}


def hash_password(password: str) -> bytes:
    """Хеширование пароля."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def verify_password(password: str, hashed_password: bytes) -> bool:
    """Проверка пароля."""
    return bcrypt.checkpw(password.encode(), hashed_password)


def user_exists(new_username: str) -> bool:
    """Проверка существования пользователя."""
    for user in users:
        if user.name == new_username:
            return True
    return False


def register_view(user_in: UserSchema) -> str:
    """Регистрация пользователя."""
    if user_exists(user_in.name):
        raise ValueError('User with this username already exists')

    hashed_password = hash_password(user_in.password)
    user = User(user_in.name, hashed_password)
    token = jwt_encode(asdict(user))
    users[user] = token
    return token


def login_view(user_in: UserSchema) -> str | None:
    """Авторизация пользователя."""
    for user in users.keys():
        if user.name == user_in.name:
            if verify_password(user_in.password, user.password):
                users[user] = jwt_encode(asdict(user))
                return users[user]
    return None
