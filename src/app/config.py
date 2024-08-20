from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent
jwt_private_path = BASE_DIR / 'jwt_tokens' / 'jwt_private.pem'
jwt_public_path = BASE_DIR / 'jwt_tokens' / 'jwt_public.pem'


class Settings(BaseSettings):
    """Настройки."""

    # Настройки JWT
    jwt_private: str = jwt_private_path.read_text()
    jwt_public: str = jwt_public_path.read_text()
    crypto_algorithm: str = 'RS256'
    jwt_auth_token_expiry_minutes: int = 10

    # Настройки Kafka
    kafka_host: str = 'kafka'
    kafka_port: str = '9092'
    kafka_instance: str = f'{kafka_host}:{kafka_port}'
    kafka_producer_topic: str = 'faces'
    file_encoding: str = 'utf-8'
    file_compression_quality: int = 1

    # Настройки db
    db_user: str = 'postgres'
    db_password: str = 'postgres'
    db_host: str = 'host.docker.internal'
    db_port: str = '5432'
    db_name: str = 'credit_card'
    db_echo: bool = False

    @property
    def db_url(self) -> str:
        """Ссылка на БД."""
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'  # noqa: E501, WPS221


settings = Settings()
