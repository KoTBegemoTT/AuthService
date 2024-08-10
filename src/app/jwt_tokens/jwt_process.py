from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings
from app.models import User


def jwt_encode(
    user: User,
    private_key: str = settings.jwt_private,
    algorithm: str = settings.crypto_algorithm,
    expire_minutes: int = settings.jwt_auth_token_expiry_minutes,
) -> str:
    """Создание токена."""
    to_encode = {'username': user.name}
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expire_minutes)

    to_encode.update(exp=expire, iat=now)  # type: ignore
    return jwt.encode(to_encode, private_key, algorithm=algorithm)


def jwt_decode(
    token: str | bytes,
    public_key: str = settings.jwt_public,
    algorithm: str = settings.crypto_algorithm,
) -> dict:
    """Расшифровка токена."""
    return jwt.decode(token, public_key, algorithms=[algorithm])
