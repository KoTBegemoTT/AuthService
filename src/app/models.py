from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """Модель пользователя."""

    username: str
    password: str
