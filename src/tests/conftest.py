import asyncio
from typing import AsyncGenerator
from unittest.mock import Mock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_helper import DatabaseHelper, db_helper
from app.db.models import BaseTable
from app.main import app

TEST_DB_URL = 'postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/test_db'  # noqa: E501
test_db_helper = DatabaseHelper(url=TEST_DB_URL, echo=True)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_db_helper.session_factory() as session:
        yield session

app.dependency_overrides[db_helper.scoped_session_dependency] = (
    override_get_async_session
)


@pytest_asyncio.fixture()
async def reset_db():
    async with test_db_helper.engine.begin() as conn:
        await conn.run_sync(BaseTable.metadata.create_all)
    yield
    async with test_db_helper.engine.begin() as conn:
        await conn.run_sync(BaseTable.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def db_helper():
    return test_db_helper


def get_redis_mock() -> Mock:
    redis_cashe: dict[str, str] = {}

    def get_token(user_id: int):
        return redis_cashe.get(f'user_id:{user_id}', None)

    def set_token(token: str, user_id: int):
        redis_cashe[f'user_id:{user_id}'] = token

    redis_client = Mock()
    redis_client.get_token = get_token
    redis_client.set_token = set_token

    redis_client.get_cache = lambda: redis_cashe

    return redis_client


@pytest.fixture
def redis_mock() -> Mock:
    return get_redis_mock()


rm = get_redis_mock()
rm.set_token('token', 1)
