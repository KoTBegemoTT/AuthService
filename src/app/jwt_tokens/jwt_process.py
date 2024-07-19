from pathlib import Path

import jwt

BASE_DIR = Path(__file__).parent.parent
jwt_private_path = BASE_DIR / "jwt_tokens" / "jwt_private.pem"
jwt_public_path = BASE_DIR / "jwt_tokens" / "jwt_public.pem"

jwt_private_key = jwt_private_path.read_text()
jwt_public_key = jwt_public_path.read_text()
crypto_algorithm = "RS256"


def jwt_encode(
    user_payload: dict,
    private_key: str = jwt_private_key,
    algorithm: str = crypto_algorithm,
) -> str:
    """Создание токена."""
    token_payload = {'name': user_payload['name']}
    return jwt.encode(token_payload, private_key, algorithm=algorithm)


def jwt_decode(
    token: str | bytes,
    public_key: str = jwt_public_key,
    algorithm: str = crypto_algorithm,
) -> dict:
    """Расшифровка токена."""
    return jwt.decode(token, public_key, algorithms=[algorithm])
