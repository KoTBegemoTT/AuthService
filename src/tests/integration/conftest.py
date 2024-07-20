import pytest
from fastapi.testclient import TestClient

from app.auth_service.views import users
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup():
    users.clear()


@pytest.fixture(scope='session')
def test_client():
    return client
