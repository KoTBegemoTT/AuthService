from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.auth_service.views import users


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup():
    users.clear()


@pytest.fixture(scope="session")
def test_client():
    return client
