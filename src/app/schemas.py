from pydantic import BaseModel


class UserSchema(BaseModel):
    """Схема пользователя."""

    name: str
    password: str


class TokenSchema(BaseModel):
    """Схема токена."""

    token: str | None
