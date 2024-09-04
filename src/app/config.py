from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent
jwt_private_path = BASE_DIR / 'jwt_tokens' / 'jwt_private.pem'
jwt_public_path = BASE_DIR / 'jwt_tokens' / 'jwt_public.pem'


class Settings(BaseSettings):
    """Настройки."""

    # Общие настройки
    service_name: str = 'auth-service'

    # Настройки JWT
    jwt_private: str = jwt_private_path.read_text()
    jwt_public: str = jwt_public_path.read_text()
    crypto_algorithm: str = 'RS256'
    jwt_auth_token_expiry_minutes: int = 10

    # Настройки Kafka
    kafka_host: str = 'kafka'
    kafka_port: str = '9092'
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
    db_schema: str = 'lebedev_schema'

    # Настройки Jaeger
    jaeger_agent_host: str = 'host.docker.internal'
    jaeger_agent_port: str = '6831'

    @property
    def db_url(self) -> str:
        """Ссылка на БД."""
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'  # noqa: E501, WPS221

    @property
    def kafka_instance(self) -> str:
        """Ссылка на kafka."""
        return f'{self.kafka_host}:{self.kafka_port}'


settings = Settings()
