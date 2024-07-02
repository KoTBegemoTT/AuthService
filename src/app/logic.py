from dataclasses import asdict

from app.jwt_process import jwt_encode
from app.models import User

users: dict[User, str] = {}


class AuthService:
    """Класс управляющий регистрацией и авторизацией."""

    @staticmethod
    def register(username: str, password: str) -> str:
        """Регистрация пользователя."""
        user = User(username=username, password=password)
        token = jwt_encode(asdict(user))
        users[user] = token
        return token

    @staticmethod
    def login(username: str, password: str) -> str | None:
        """Авторизация пользователя."""
        user = User(username=username, password=password)
        if user in users:
            token = jwt_encode(asdict(user))
            users[user] = token
            return token
        return None
