from dataclasses import asdict

from app.jwt_process import jwt_encode
from app.models import User

users: dict[User, str] = {}


class AuthService:
    """Класс управляющий регистрацией и авторизацией."""

    @staticmethod
    def user_exists(username: str) -> bool:
        """Проверка существования пользователя."""
        for user in users:
            if user.username == username:
                return True
        return False

    @staticmethod
    def register(username: str, password: str) -> str:
        """Регистрация пользователя."""
        if AuthService.user_exists(username):
            raise ValueError("User with this username already exists")

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
