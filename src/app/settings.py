from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent
jwt_private_path = BASE_DIR / 'jwt_tokens' / 'jwt_private.pem'
jwt_public_path = BASE_DIR / 'jwt_tokens' / 'jwt_public.pem'


class Settings(BaseSettings):
    """Настройки."""

    jwt_private: str = jwt_private_path.read_text()
    jwt_public: str = jwt_public_path.read_text()
    crypto_algorithm: str = 'RS256'
    jwt_auth_token_expiry_minutes: int = 10


settings = Settings()
