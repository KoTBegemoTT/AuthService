import pytest_asyncio
from httpx import AsyncClient

from app.main import app


@pytest_asyncio.fixture(scope='session')
async def ac():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac
