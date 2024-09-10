import redis
from app.config import settings


class BaseRedisClient:
    """Базовый класс для работы с Redis."""

    def __init__(self, host, port, db_number) -> None:
        self.client = redis.Redis(host=host, port=port, db=db_number)

    def close(self):
        """Закрытие соединения с Redis."""
        self.client.close()

    def set(self, key, value):
        """Установка значения по ключу."""
        self.client.set(key, value)

    def get(self, key):
        """Получение значения по ключу."""
        return self.client.get(key)


class RedisClient(BaseRedisClient):
    """Класс для работы с Redis."""

    def get_token(self, user_id: int):
        """Получение токена."""
        return self.get(f'user_id:{user_id}')

    def set_token(self, token: str, user_id: int):
        """Установка id типа транзакции."""
        self.set(f'user_id:{user_id}', token)


redis_client = RedisClient(
    settings.redis_host,
    settings.redis_port,
    settings.redis_db_number,
)


def get_redis_client():
    """Получение экземпляра RedisClient."""
    return redis_client
