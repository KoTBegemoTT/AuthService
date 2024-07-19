from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """Модель пользователя."""

    name: str
    password: bytes
