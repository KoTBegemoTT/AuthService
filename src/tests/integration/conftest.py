import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.auth_service.views import user_tokens, users
from app.main import app


@pytest.fixture(autouse=True)
def setup():
    users.clear()
    user_tokens.clear()


@pytest_asyncio.fixture(scope='session')
async def ac():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac
