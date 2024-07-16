import pytest

from src.app.auth_service.logic import users


@pytest.fixture(autouse=True)
def setup():
    users.clear()
