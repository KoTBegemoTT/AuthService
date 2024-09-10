import pytest_asyncio
from httpx import AsyncClient

from app.external.redis_client import get_redis_client
from app.main import app
from tests.conftest import get_redis_mock

app.dependency_overrides[get_redis_client] = (
    get_redis_mock
)


@pytest_asyncio.fixture(scope='session')
async def ac():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac
